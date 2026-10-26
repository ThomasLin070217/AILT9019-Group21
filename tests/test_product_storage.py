import copy,json,sqlite3,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from uuid import uuid4
import test_album_store as fixtures
from album_store import ConflictError

class PhotoTests(unittest.TestCase):
 def setUp(self):fixtures.AlbumTests.setUp(self)
 def tearDown(self):fixtures.AlbumTests.tearDown(self)
 def test_rejected_creation_does_not_recurse_or_leave_files(self):
  with self.store.connect() as c:c.execute("CREATE TRIGGER reject_create BEFORE INSERT ON trips BEGIN SELECT RAISE(ABORT,'disk failure'); END")
  with self.assertRaises(sqlite3.IntegrityError):self.store.create(self.data)
  self.assertEqual(self.store.list(),[]);self.assertEqual(list((self.store.directory/'media').iterdir()),[])
 def test_photo_replacement_identity_retry_and_stale_edit(self):
  trip=self.store.create(self.data);old=self.store.photo_path(trip['photos'][0]['url'])
  data={'expected_revision':1,'request_id':str(uuid4()),'photos':self.data['photos']}
  updated=self.store.replace_photos(trip['id'],data)
  self.assertEqual(updated['id'],trip['id']);self.assertEqual(updated['notes'],trip['notes']);self.assertEqual(updated['revision'],2)
  self.assertEqual(self.store.replace_photos(trip['id'],data),updated);self.assertEqual(len(self.store.list()),1)
  self.assertFalse(old.exists());self.assertIsNone(self.store.photo_path(trip['photos'][0]['url']))
  with self.assertRaises(ConflictError):self.store.replace_photos(trip['id'],{**data,'request_id':str(uuid4())})
 def test_partial_photo_write_and_database_failure_preserve_original(self):
  trip=self.store.create(self.data);folder=self.store.directory/'media'/trip['id'];original=set(folder.iterdir())
  data={'expected_revision':1,'request_id':str(uuid4()),'photos':self.data['photos']*2}
  write=Path.write_bytes
  def partial(path,raw):write(path,raw[:10]);raise OSError('disk full')
  with patch.object(Path,'write_bytes',partial):
   with self.assertRaises(OSError):self.store.replace_photos(trip['id'],data)
  self.assertEqual(set(folder.iterdir()),original);self.assertEqual(self.store.list(),[trip])
  with self.store.connect() as c:c.execute("CREATE TRIGGER reject_photos BEFORE UPDATE ON trips BEGIN SELECT RAISE(ABORT,'disk failure'); END")
  with self.assertRaises(sqlite3.IntegrityError):self.store.replace_photos(trip['id'],data)
  self.assertEqual(set(folder.iterdir()),original);self.assertEqual(self.store.list(),[trip])

class AIHttpTests(unittest.TestCase):
 def setUp(self):fixtures.HttpTests.setUp(self)
 def tearDown(self):fixtures.HttpTests.tearDown(self)
 def test_consent_and_stale_revision_block_provider(self):
  trip=self.store.create(self.data);url=self.base+'/api/trips/'+trip['id']+'/generate'
  with patch('serve.generate') as generate:
   for data,status in [({'expected_revision':1,'consent':False},400),({'expected_revision':0,'consent':True},409)]:
    request=Request(url,json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with self.assertRaises(HTTPError) as error:urlopen(request)
    self.assertEqual(error.exception.code,status)
   generate.assert_not_called()
   def concurrent(*args):self.store.edit(trip['id'],{'notes':'Newer notes','expected_revision':1});return {'status':'draft'}
   generate.side_effect=concurrent
   with self.assertRaises(HTTPError) as error:urlopen(Request(url,b'{"expected_revision":1,"consent":true}',headers={'Content-Type':'application/json'}))
   self.assertEqual(error.exception.code,409);self.assertEqual(self.store.get(trip['id'])['notes'],'Newer notes')
