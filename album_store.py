"""Local trip creation and photo storage. No cloud services are used."""
import base64
import hashlib
import io
import json
import re
import shutil
import sqlite3
import warnings
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from uuid import UUID, uuid4

MAX_PHOTOS = 5
MAX_PHOTO_BYTES = 5 * 1024 * 1024
MAX_TOTAL_BYTES = 20 * 1024 * 1024
MAX_REQUEST_BYTES = 28 * 1024 * 1024


class ValidationError(ValueError):
    pass


class ConflictError(ValueError):
    pass


class NotFoundError(LookupError):
    pass


def trip_date_field(value):
    if value is not None:
        try:
            if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
                raise ValueError()
        except ValueError:
            raise ValidationError('Use a valid YYYY-MM-DD date, or leave it empty.') from None
    return value


def text_field(data, name, limit):
    value = data.get(name, '')
    if not isinstance(value, str) or len(value) > limit:
        raise ValidationError(f'{name} must be text of at most {limit} characters.')
    return value.strip()


class AlbumStore:
    def __init__(self, directory, cities):
        self.directory = Path(directory).resolve()
        self.cities = {city['id']: city for city in cities}

    @contextmanager
    def connect(self):
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        connection = sqlite3.connect(self.directory / 'album.sqlite3', timeout=10)
        try:
            connection.execute('''CREATE TABLE IF NOT EXISTS trips (
                id TEXT PRIMARY KEY, request_id TEXT NOT NULL UNIQUE,
                request_hash TEXT NOT NULL, snapshot TEXT NOT NULL,
                deleted INTEGER NOT NULL DEFAULT 0)''')
            if 'deleted' not in {row[1] for row in connection.execute('PRAGMA table_info(trips)')}:
                connection.execute('BEGIN IMMEDIATE')
                if 'deleted' not in {row[1] for row in connection.execute('PRAGMA table_info(trips)')}:
                    connection.execute('ALTER TABLE trips ADD COLUMN deleted INTEGER NOT NULL DEFAULT 0')
                connection.commit()
            with connection:
                yield connection
        finally:
            connection.close()

    def list(self):
        with self.connect() as connection:
            rows = [json.loads(row[0]) for row in connection.execute('SELECT snapshot FROM trips WHERE deleted=0 ORDER BY rowid')]
            deleted = [row[0] for row in connection.execute('SELECT id FROM trips WHERE deleted>0')]
        for trip_id in deleted:
            self.cleanup_photos(trip_id)
        for trip in rows:
            if trip.get('photo_update_id'):
                try:self.cleanup_unused_photos(trip['id'])
                except (OSError,sqlite3.Error):pass
        return rows

    def get(self, trip_id):
        with self.connect() as connection:
            row = connection.execute('SELECT snapshot FROM trips WHERE id=? AND deleted=0', (trip_id,)).fetchone()
        if row is None:
            raise NotFoundError('This trip no longer exists. Refresh the album.')
        return json.loads(row[0])

    def decode_photos(self, photos):
        if not isinstance(photos, list) or not 1 <= len(photos) <= MAX_PHOTOS:
            raise ValidationError(f'Choose between 1 and {MAX_PHOTOS} photos.')
        # Validate and decode every image before creating files or a trip record.
        images, total = [], 0
        for photo in photos:
            if not isinstance(photo, dict):
                raise ValidationError('Each photo must contain image data.')
            encoded = photo.get('data')
            if not isinstance(encoded, str) or len(encoded) > (MAX_PHOTO_BYTES + 2) // 3 * 4:
                raise ValidationError('Each photo must be at most 5 MB.')
            try:
                raw = base64.b64decode(encoded, validate=True)
            except ValueError:
                raise ValidationError('The photo upload is damaged. Choose the file again.') from None
            total += len(raw)
            if len(raw) > MAX_PHOTO_BYTES or total > MAX_TOTAL_BYTES:
                raise ValidationError('Use photos up to 5 MB each and 20 MB in total.')
            images.append(self.clean_image(raw))
        return images

    def create(self, data):
        if not isinstance(data, dict):
            raise ValidationError('Send a trip object.')
        request_id = data.get('request_id')
        try:
            UUID(request_id)
        except (ValueError, TypeError, AttributeError):
            raise ValidationError('A valid request_id is required for safe retries.') from None
        digest = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=True).encode()).hexdigest()
        with self.connect() as connection:
            previous = connection.execute('SELECT request_hash, snapshot, deleted FROM trips WHERE request_id=?', (request_id,)).fetchone()
        if previous:
            if previous[2]:
                raise ConflictError('This trip was already deleted. Refresh the album before creating a new visit.')
            if previous[0] != digest:
                raise ConflictError('This save already completed with different content. Refresh your album before creating another trip.')
            return json.loads(previous[1])
        city_id = data.get('city_id')
        if not isinstance(city_id, str) or city_id not in self.cities:
            raise ValidationError('Choose a supported city.')
        trip_date = trip_date_field(data.get('trip_date'))
        title = text_field(data, 'title', 200)
        notes = text_field(data, 'notes', 5000)
        images = self.decode_photos(data.get('photos'))
        trip_id = str(uuid4())
        media = self.directory / 'media'
        media.mkdir(exist_ok=True, mode=0o700)
        folder = media / trip_id
        folder.mkdir(mode=0o700)
        snapshot = {'id': trip_id, 'city_id': city_id, 'trip_date': trip_date,
                    'title': title or f'A visit to {self.cities[city_id]["name"]}',
                    'notes': notes, 'memory_text': '', 'photos': [], 'source': 'user', 'revision': 1}
        try:
            for image_bytes in images:
                photo_id = str(uuid4())
                (folder / f'{photo_id}.jpg').write_bytes(image_bytes)
                snapshot['photos'].append({'id': photo_id, 'url': f'/media/{trip_id}/{photo_id}.jpg', 'alt': 'Trip photograph'})
            with self.connect() as connection:
                connection.execute('INSERT INTO trips (id, request_id, request_hash, snapshot) VALUES (?, ?, ?, ?)',
                                   (trip_id, request_id, digest, json.dumps(snapshot)))
        except sqlite3.IntegrityError:
            shutil.rmtree(folder)
            # Only retry a genuine concurrent request collision. Persistent DB
            # failures (e.g. a rejected insert) must not recurse indefinitely.
            with self.connect() as connection:
                collision = connection.execute('SELECT 1 FROM trips WHERE request_id=?', (request_id,)).fetchone()
            if collision:
                return self.create(data)
            raise
        except Exception:
            shutil.rmtree(folder)
            raise
        return snapshot

    def edit(self, trip_id, data):
        if not isinstance(data, dict) or set(data) - {'title', 'trip_date', 'notes', 'memory_text', 'expected_revision'}:
            raise ValidationError('Only title, date, notes and reviewed memory text can be edited. City, identity and photos stay unchanged.')
        revision = data.get('expected_revision')
        if type(revision) is not int or revision < 0:
            raise ValidationError('A valid expected_revision is required. Refresh the saved trip and try again.')
        patch = {}
        for field, limit in [('title', 200), ('notes', 5000), ('memory_text', 5000)]:
            if field in data:
                patch[field] = text_field(data, field, limit)
        if 'trip_date' in data:
            patch['trip_date'] = trip_date_field(data['trip_date'])
        if not patch:
            raise ValidationError('Provide a title, date or notes to edit.')
        with self.connect() as connection:
            # Serialize the read/check/write so two tabs cannot overwrite each other.
            connection.execute('BEGIN IMMEDIATE')
            row = connection.execute('SELECT snapshot FROM trips WHERE id=? AND deleted=0', (trip_id,)).fetchone()
            if row is None:
                raise NotFoundError('This trip no longer exists. Refresh the album to check your saved records.')
            snapshot = json.loads(row[0])
            current_revision = snapshot.get('revision', 0)
            if 'title' in patch and not patch['title']:
                patch['title'] = f'A visit to {self.cities[snapshot["city_id"]]["name"]}'
            unchanged = all(snapshot.get(key) == value for key, value in patch.items())
            if revision != current_revision:
                if unchanged and revision + 1 == current_revision:
                    return snapshot  # A retry of the last successful edit.
                raise ConflictError('This trip changed in another tab. Your draft is kept. Reload the saved version before editing again.')
            if unchanged:
                return snapshot
            snapshot.update(patch)
            snapshot['revision'] = current_revision + 1
            connection.execute('UPDATE trips SET snapshot=? WHERE id=?', (json.dumps(snapshot), trip_id))
            return snapshot

    def remove(self, trip_id, data):
        if not isinstance(data, dict) or set(data) != {'expected_revision'}:
            raise ValidationError('Provide only expected_revision to confirm the version being deleted.')
        revision = data['expected_revision']
        if type(revision) is not int or revision < 0:
            raise ValidationError('A valid expected_revision is required. Refresh the trip before deleting it.')
        with self.connect() as connection:
            connection.execute('BEGIN IMMEDIATE')
            row = connection.execute('SELECT snapshot, deleted FROM trips WHERE id=?', (trip_id,)).fetchone()
            if row is None:
                raise NotFoundError('This trip was not found. Refresh the album before trying again.')
            if not row[1]:
                snapshot = json.loads(row[0])
                if snapshot.get('revision', 0) != revision:
                    raise ConflictError('This trip changed in another tab. Refresh the album and review the latest trip before deleting it.')
                # Retain just identity/request metadata to make retries safe. Personal
                # text and photo references are removed in the same transaction.
                connection.execute("UPDATE trips SET snapshot='{}', deleted=? WHERE id=?", (revision + 1, trip_id))
        # Only touch files after the database commit. A failed commit leaves the
        # original record and all its photos intact. Deleted media is denied even
        # if the OS temporarily prevents cleanup; reads/retries attempt it again.
        return {'id': trip_id, 'deleted': True, 'cleanup_pending': not self.cleanup_photos(trip_id)}

    def replace_photos(self, trip_id, data):
        if not isinstance(data, dict) or set(data) != {'expected_revision','request_id','photos'} or type(data.get('expected_revision')) is not int or data['expected_revision'] < 0:
            raise ValidationError('Provide photos, expected_revision and a new request_id.')
        try:UUID(data['request_id'])
        except (ValueError, TypeError, AttributeError):raise ValidationError('Invalid photo update request ID.') from None
        images = self.decode_photos(data['photos'])
        digest = hashlib.sha256(b''.join(images)).hexdigest()
        written = []
        try:
            with self.connect() as connection:
                connection.execute('BEGIN IMMEDIATE')
                row = connection.execute('SELECT snapshot FROM trips WHERE id=? AND deleted=0',(trip_id,)).fetchone()
                if row is None:raise NotFoundError('This trip no longer exists. Refresh your album.')
                trip = json.loads(row[0])
                if trip.get('photo_update_id') == data['request_id']:
                    if trip.get('photo_update_hash') != digest:raise ConflictError('This photo request already saved different photos. Refresh the trip.')
                    return trip
                if trip.get('revision',0) != data['expected_revision']:raise ConflictError('The trip changed. Refresh it before replacing photos; your selected files are kept.')
                photos=[];folder=self.directory/'media'/trip_id;folder.mkdir(parents=True,exist_ok=True,mode=0o700)
                for raw in images:
                    photo_id=str(uuid4());path=folder/f'{photo_id}.jpg';written.append(path);path.write_bytes(raw)
                    photos.append({'id':photo_id,'url':f'/media/{trip_id}/{photo_id}.jpg','alt':'Trip photograph'})
                trip.update(photos=photos,revision=trip.get('revision',0)+1,photo_update_id=data['request_id'],photo_update_hash=digest)
                connection.execute('UPDATE trips SET snapshot=? WHERE id=?',(json.dumps(trip),trip_id))
        except Exception:
            for path in written:path.unlink(missing_ok=True)
            raise
        try:self.cleanup_unused_photos(trip_id)
        except (OSError,sqlite3.Error):pass
        return trip

    def cleanup_unused_photos(self, trip_id):
        with self.connect() as connection:
            connection.execute('BEGIN IMMEDIATE')
            row=connection.execute('SELECT snapshot FROM trips WHERE id=? AND deleted=0',(trip_id,)).fetchone()
            if row is None:return
            keep={photo['id']+'.jpg' for photo in json.loads(row[0])['photos']}
            folder=self.directory/'media'/trip_id
            if folder.is_symlink():return
            for path in folder.glob('*.jpg'):
                if path.name not in keep:
                    try:path.unlink()
                    except OSError:pass

    def cleanup_photos(self, trip_id):
        if not re.fullmatch(r'[0-9a-f-]{36}', trip_id):
            return False
        folder = self.directory / 'media' / trip_id
        if folder.is_symlink():
            return False
        try:
            shutil.rmtree(folder)
        except FileNotFoundError:
            pass
        except OSError:
            return False
        return True

    @staticmethod
    def clean_image(raw):
        try:
            from PIL import Image, ImageOps, UnidentifiedImageError
        except ImportError:
            raise RuntimeError('Photo support is missing. Run: python3 -m pip install -r requirements.txt') from None
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(raw)) as image:
                    if image.format not in {'JPEG', 'PNG', 'WEBP'}:
                        raise ValidationError('Use a JPEG, PNG or WebP photo.')
                    if image.width * image.height > 25_000_000:
                        raise ValidationError('Photos must be at most 25 megapixels.')
                    if getattr(image, 'n_frames', 1) != 1:
                        raise ValidationError('Use a still photo, not an animated image.')
                    image.load()
                    oriented = ImageOps.exif_transpose(image)
                    # Copy only pixels; discard EXIF/GPS and other embedded metadata.
                    rgba = oriented.convert('RGBA')
                    clean = Image.new('RGB', rgba.size, 'white')
                    clean.paste(rgba, mask=rgba.getchannel('A'))
                    clean.thumbnail((4096, 4096))
                    output = io.BytesIO()
                    clean.save(output, 'JPEG', quality=90)
                    return output.getvalue()
        except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning, ValueError):
            raise ValidationError('A photo could not be read. Use a valid JPEG, PNG or WebP, up to 25 megapixels.') from None

    def photo_path(self, path):
        if not re.fullmatch(r'/media/[0-9a-f-]{36}/[0-9a-f-]{36}\.jpg', path):
            return None
        trip_id = path.split('/')[2]
        with self.connect() as connection:
            row = connection.execute('SELECT snapshot FROM trips WHERE id=? AND deleted=0', (trip_id,)).fetchone()
        if row is None or not any(photo.get('url') == path for photo in json.loads(row[0])['photos']):
            return None
        target = (self.directory / path.lstrip('/')).resolve()
        media = (self.directory / 'media').resolve()
        return target if target.is_relative_to(media) and target.is_file() else None
