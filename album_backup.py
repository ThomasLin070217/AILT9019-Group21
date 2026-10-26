"""Portable ZIP backups; restore merges without overwriting existing memories."""
import hashlib
import io
import json
import shutil
import zipfile
from pathlib import PurePosixPath
from uuid import UUID, uuid4

from album_store import ValidationError, ConflictError, text_field, trip_date_field

MAX_BACKUP_BYTES = 100 * 1024 * 1024
MAX_EXPANDED_BYTES = 200 * 1024 * 1024


class AlbumBackup:
    def __init__(self, store):
        self.store = store

    def export(self):
        output = io.BytesIO()
        with self.store.connect() as connection:
            connection.execute('BEGIN IMMEDIATE')
            trips = [json.loads(row[0]) for row in connection.execute('SELECT snapshot FROM trips WHERE deleted=0')]
            if len(trips) > 500:
                raise ValidationError('This album exceeds the 500-trip ZIP limit. Copy the complete local album folder instead.')
            hashes, total = {}, 0
            with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
                for trip in trips:
                    for photo in trip['photos']:
                        name = photo['url'].lstrip('/')
                        raw = (self.store.directory / name).read_bytes()
                        total += len(raw)
                        if total > MAX_EXPANDED_BYTES:
                            raise ValidationError('This album exceeds the 200 MB backup limit. Copy the complete local album folder instead.')
                        hashes[name] = hashlib.sha256(raw).hexdigest()
                        archive.writestr(name, raw)
                archive.writestr('album.json', json.dumps({'format': 'travel-memory-map', 'version': 1, 'trips': trips, 'sha256': hashes}, ensure_ascii=False))
        if len(output.getvalue()) > MAX_BACKUP_BYTES:
            raise ValidationError('This backup exceeds 100 MB. Copy the complete local album folder instead.')
        return output.getvalue()

    def parse(self, raw):
        if not raw or len(raw) > MAX_BACKUP_BYTES:
            raise ValidationError('Choose an album ZIP up to 100 MB.')
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                infos = archive.infolist()
                names = [info.filename for info in infos]
                if len(infos) > 3001 or len(names) != len(set(names)) or sum(info.file_size for info in infos) > MAX_EXPANDED_BYTES:
                    raise ValidationError('Backup has duplicate entries or exceeds the file/size limits.')
                if any(info.flag_bits & 1 or info.is_dir() or '..' in PurePosixPath(info.filename).parts or info.filename.startswith('/') or '\\' in info.filename for info in infos):
                    raise ValidationError('Backup contains unsupported file paths or encrypted entries.')
                manifest = json.loads(archive.read('album.json'))
                if not isinstance(manifest, dict) or manifest.get('format') != 'travel-memory-map' or manifest.get('version') != 1:
                    raise ValidationError('This is not a supported Travel Memory Map backup.')
                trips, hashes = manifest.get('trips'), manifest.get('sha256')
                if not isinstance(trips, list) or len(trips) > 500 or not isinstance(hashes, dict):
                    raise ValidationError('Backup must contain at most 500 valid trips.')
                seen, images = set(), {}
                for trip in trips:
                    if not isinstance(trip, dict) or not {'id','city_id','trip_date','title','notes','memory_text','photos'} <= set(trip):
                        raise ValidationError('Invalid trip in backup.')
                    trip_id = trip.get('id')
                    if str(UUID(trip_id)) != trip_id or trip_id in seen or trip.get('city_id') not in self.store.cities:
                        raise ValidationError('Backup has an invalid/duplicate trip or unsupported city.')
                    seen.add(trip_id)
                    for field, limit in [('title', 200), ('notes', 5000), ('memory_text', 5000)]:
                        text_field(trip, field, limit)
                    trip_date_field(trip.get('trip_date'))
                    photos = trip.get('photos')
                    if not isinstance(photos, list) or not 1 <= len(photos) <= 5:
                        raise ValidationError('Each restored trip needs 1–5 photos.')
                    for photo in photos:
                        photo_id = photo.get('id')
                        if str(UUID(photo_id)) != photo_id or photo.get('url') != f'/media/{trip_id}/{photo_id}.jpg':
                            raise ValidationError('Invalid photo reference in backup.')
                        name = photo['url'].lstrip('/')
                        if name in images:
                            raise ValidationError('Duplicate photo in backup.')
                        image = archive.read(name)
                        if hashlib.sha256(image).hexdigest() != hashes.get(name):
                            raise ValidationError('A backup photo is missing or damaged (checksum mismatch).')
                        # Decode actual bytes, applying the same limits as uploads.
                        self.store.clean_image(image)
                        images[name] = image
                if set(names) != {'album.json', *images} or set(hashes) != set(images):
                    raise ValidationError('Backup contains missing or unexpected files.')
                return trips, images
        except (ValidationError,):
            raise
        except (ValueError, TypeError, KeyError, AttributeError, zipfile.BadZipFile, RuntimeError, OSError):
            raise ValidationError('The backup could not be read. Choose a complete, valid album ZIP.') from None

    @staticmethod
    def equivalent(first, second):
        fields = ['id', 'city_id', 'trip_date', 'title', 'notes', 'memory_text', 'photos']
        return all(first.get(field) == second.get(field) for field in fields)

    def preview(self, raw):
        trips, _ = self.parse(raw)
        with self.store.connect() as connection:
            existing = {row[0]: (json.loads(row[1]), row[2]) for row in connection.execute('SELECT id, snapshot, deleted FROM trips')}
        conflicts, unchanged = [], 0
        for trip in trips:
            current = existing.get(trip['id'])
            if current:
                if not current[1] and self.equivalent(current[0], trip):
                    unchanged += 1
                else:
                    conflicts.append(trip['title'])
        return {'total': len(trips), 'new': len(trips) - len(conflicts) - unchanged, 'unchanged': unchanged, 'conflicts': len(conflicts), 'conflict_titles': conflicts[:10]}

    def restore(self, raw, copies=False):
        trips, images = self.parse(raw)
        added, skipped, folders = [], 0, []
        try:
            with self.store.connect() as connection:
                connection.execute('BEGIN IMMEDIATE')
                for incoming in trips:
                    existing = connection.execute('SELECT snapshot, deleted FROM trips WHERE id=?', (incoming['id'],)).fetchone()
                    if existing and not existing[1] and self.equivalent(json.loads(existing[0]), incoming):
                        skipped += 1
                        continue
                    if existing and not copies:
                        raise ConflictError('Some backup trips differ from existing or deleted trips. Choose “Import conflicts as new trips” to keep both.')
                    trip_id = str(uuid4()) if existing else incoming['id']
                    trip = {field: incoming[field] for field in ['city_id', 'trip_date', 'title', 'notes', 'memory_text']}
                    trip.update(id=trip_id, revision=1, source='user', photos=[])
                    folder = self.store.directory / 'media' / trip_id
                    folder.parent.mkdir(exist_ok=True, mode=0o700)
                    if folder.exists():
                        raise ConflictError('A local photo folder conflicts with this backup. Choose another storage directory to restore safely.')
                    folder.mkdir(mode=0o700);folders.append(folder)
                    for photo in incoming['photos']:
                        photo_id = str(uuid4()) if existing else photo['id']
                        (folder / f'{photo_id}.jpg').write_bytes(images[photo['url'].lstrip('/')])
                        trip['photos'].append({'id': photo_id, 'url': f'/media/{trip_id}/{photo_id}.jpg', 'alt': 'Trip photograph'})
                    connection.execute('INSERT INTO trips (id,request_id,request_hash,snapshot) VALUES (?,?,?,?)', (trip_id, str(uuid4()), 'restored', json.dumps(trip)))
                    added.append(trip)
        except Exception:
            for folder in folders:
                shutil.rmtree(folder)
            raise
        return {'imported': len(added), 'skipped': skipped, 'trips': added}
