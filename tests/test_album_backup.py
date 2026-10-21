import copy
import io
import json
from pathlib import Path
import sqlite3
import zipfile
import unittest

from album_backup import AlbumBackup
from album_store import AlbumStore, ValidationError, ConflictError
import test_album_store as album_fixtures


class BackupTests(unittest.TestCase):
    def setUp(self):album_fixtures.AlbumTests.setUp(self)
    def tearDown(self):album_fixtures.AlbumTests.tearDown(self)

    def target(self):return AlbumStore(Path(self.temp.name)/'restored',self.cities)

    def test_roundtrip_reconstructs_photos_text_and_idempotent_merge(self):
        trip=self.store.create(self.data);self.store.edit(trip['id'],{'memory_text':'Reviewed memory','expected_revision':1})
        raw=AlbumBackup(self.store).export();target=self.target();backup=AlbumBackup(target)
        self.assertEqual(backup.preview(raw)['new'],1);self.assertEqual(backup.restore(raw)['imported'],1)
        restored=target.list()[0];self.assertEqual(restored['id'],trip['id']);self.assertEqual(restored['memory_text'],'Reviewed memory')
        self.assertTrue(target.photo_path(restored['photos'][0]['url']).exists())
        self.assertEqual(backup.restore(raw)['skipped'],1);self.assertEqual(len(target.list()),1)

    def test_conflicts_never_overwrite_and_can_restore_as_copy(self):
        trip=self.store.create(self.data);raw=AlbumBackup(self.store).export();self.store.edit(trip['id'],{'notes':'Newer notes','expected_revision':1})
        backup=AlbumBackup(self.store);self.assertEqual(backup.preview(raw)['conflicts'],1)
        with self.assertRaises(ConflictError):backup.restore(raw)
        self.assertEqual(self.store.list()[0]['notes'],'Newer notes')
        self.assertEqual(backup.restore(raw,copies=True)['imported'],1);self.assertEqual(len(self.store.list()),2)

    def test_invalid_archives_and_hash_mismatch_leave_album_untouched(self):
        trip=self.store.create(self.data);raw=AlbumBackup(self.store).export()
        for bad in [b'not zip',self.repack(raw,extra=('../escape','bad')),self.repack(raw,corrupt=True)]:
            with self.assertRaises(ValidationError):AlbumBackup(self.target()).restore(bad)
            self.assertEqual(self.target().list(),[])
        self.assertEqual(len(self.store.list()),1)

    @staticmethod
    def repack(raw,extra=None,corrupt=False):
        output=io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(raw)) as original,zipfile.ZipFile(output,'w') as target:
            for name in original.namelist():
                data=original.read(name)
                if corrupt and name.endswith('.jpg'):data+=b'corrupt'
                target.writestr(name,data)
            if extra:target.writestr(*extra)
        return output.getvalue()

    def test_restore_failure_rolls_back_files_and_records(self):
        self.store.create(self.data);raw=AlbumBackup(self.store).export();target=self.target()
        with target.connect() as connection:connection.execute("CREATE TRIGGER reject_restore BEFORE INSERT ON trips BEGIN SELECT RAISE(ABORT, 'disk failure'); END")
        with self.assertRaises(sqlite3.IntegrityError):AlbumBackup(target).restore(raw)
        self.assertEqual(target.list(),[]);self.assertEqual(list((target.directory/'media').iterdir()),[])

    def test_deleted_trip_requires_explicit_copy_and_no_secrets_in_backup(self):
        trip=self.store.create(self.data);raw=AlbumBackup(self.store).export();self.store.remove(trip['id'],{'expected_revision':1})
        with self.assertRaises(ConflictError):AlbumBackup(self.store).restore(raw)
        self.assertEqual(AlbumBackup(self.store).restore(raw,copies=True)['imported'],1)
        self.assertNotEqual(self.store.list()[0]['id'],trip['id'])
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:self.assertEqual(set(archive.namelist()),{'album.json',trip['photos'][0]['url'].lstrip('/')})
