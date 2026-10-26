"""Real images, SQLite persistence, failed saves and loopback HTTP contracts."""
import base64
import copy
import io
import json
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

from PIL import Image
from album_store import AlbumStore, ValidationError, ConflictError, NotFoundError, MAX_REQUEST_BYTES
from serve import Handler, ROOT


def image_data():
    output=io.BytesIO()
    image=Image.new('RGB',(80,60),'green')
    exif=Image.Exif();exif[270]='Private image metadata'
    image.save(output,'JPEG',exif=exif)
    return base64.b64encode(output.getvalue()).decode()


class AlbumTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.cities=json.loads((ROOT/'data/cities.json').read_text())
        self.store=AlbumStore(self.temp.name,self.cities)
        self.data={'request_id':str(uuid4()),'city_id':'jp-osaka','trip_date':'2026-10-20',
                   'title':'真实旅行 <text>','notes':'自己的随笔','photos':[{'data':image_data()}]}

    def tearDown(self):
        self.temp.cleanup()

    def test_saved_trip_and_photos_survive_store_reconstruction(self):
        saved=self.store.create(self.data)
        self.assertEqual(AlbumStore(self.temp.name,self.cities).list(),[saved])
        self.assertEqual(saved['notes'],'自己的随笔')
        self.assertEqual(saved['source'],'user')
        with Image.open(self.store.photo_path(saved['photos'][0]['url'])) as image:
            self.assertEqual(image.size,(80,60))
            self.assertEqual(dict(image.getexif()),{})

    def test_retry_is_idempotent_but_new_visit_has_own_identity(self):
        saved=self.store.create(self.data)
        self.assertEqual(self.store.create(self.data),saved)
        self.assertEqual(len(self.store.list()),1)
        self.data['request_id']=str(uuid4())
        self.assertNotEqual(self.store.create(self.data)['id'],saved['id'])
        self.assertEqual(len(self.store.list()),2)

    def test_changed_retry_reports_conflict(self):
        self.store.create(self.data);self.data['notes']='changed'
        with self.assertRaises(ConflictError):self.store.create(self.data)
        self.assertEqual(len(self.store.list()),1)

    def test_invalid_inputs_create_no_trip(self):
        for field,value in [('city_id','unknown'),('city_id',[]),('trip_date','2026-02-30'),
                            ('trip_date','20261020'),('title','x'*201),('notes','x'*5001),
                            ('photos',[]),('photos',[{'data':'not base64'}]),
                            ('photos',[{'data':base64.b64encode(b'not an image').decode()}]),
                            ('request_id','invalid')]:
            with self.subTest(field=field,value=str(value)[:30]):
                data=copy.deepcopy(self.data);data[field]=value
                with self.assertRaises(ValidationError):self.store.create(data)
                self.assertEqual(self.store.list(),[])

    def test_optional_title_date_and_notes(self):
        self.data.update(title='',notes='',trip_date=None)
        saved=self.store.create(self.data)
        self.assertEqual(saved['title'],'A visit to Osaka')
        self.assertIsNone(saved['trip_date'])

    def test_photo_limit_and_animated_images(self):
        self.data['photos']*=6
        with self.assertRaises(ValidationError):self.store.create(self.data)
        output=io.BytesIO();Image.new('RGB',(20,20)).save(output,'GIF')
        with self.assertRaises(ValidationError):self.store.clean_image(output.getvalue())
        self.assertEqual(self.store.list(),[])

    def test_partial_file_failure_rolls_back(self):
        self.data['photos']*=2
        original=Path.write_bytes
        calls=[]
        def fail_second(path,content):
            calls.append(path)
            if len(calls)==2:raise OSError('disk full')
            return original(path,content)
        with patch.object(Path,'write_bytes',fail_second):
            with self.assertRaises(OSError):self.store.create(self.data)
        self.assertEqual(self.store.list(),[])
        self.assertEqual(list((Path(self.temp.name)/'media').iterdir()),[])

    def test_media_cannot_escape_store(self):
        self.assertIsNone(self.store.photo_path('/media/../../album.sqlite3'))
        self.assertIsNone(self.store.photo_path('/media/missing.jpg'))

    def test_edit_keeps_trip_identity_and_photo_bytes(self):
        trip=self.store.create(self.data)
        photo=self.store.photo_path(trip['photos'][0]['url']);original=photo.read_bytes()
        updated=self.store.edit(trip['id'],{'title':'新标题','notes':'新的随笔','trip_date':'2026-09-30','expected_revision':1})
        for field in ['id','city_id','photos','memory_text','source']:self.assertEqual(updated[field],trip[field])
        self.assertEqual(updated['revision'],2)
        self.assertEqual(photo.read_bytes(),original)
        self.assertEqual(AlbumStore(self.temp.name,self.cities).list(),[updated])

    def test_invalid_edits_preserve_saved_trip(self):
        trip=self.store.create(self.data)
        for patch in [{'id':'changed'},{'city_id':'jp-tokyo'},{'photos':[]},{'title':None},
                      {'notes':'x'*5001},{'trip_date':'2026-02-30'},{'trip_date':'20261020'},
                      {'expected_revision':True},{'expected_revision':-1}]:
            with self.subTest(patch=str(patch)[:60]):
                with self.assertRaises(ValidationError):self.store.edit(trip['id'],{'expected_revision':1,**patch})
                self.assertEqual(self.store.list(),[trip])
        with self.assertRaises(NotFoundError):self.store.edit(str(uuid4()),{'title':'unknown','expected_revision':1})

    def test_edit_retry_and_conflict(self):
        trip=self.store.create(self.data);patch={'title':'Updated','expected_revision':1}
        updated=self.store.edit(trip['id'],patch)
        self.assertEqual(self.store.edit(trip['id'],patch),updated)
        with self.assertRaises(ConflictError):self.store.edit(trip['id'],{'notes':'stale edit','expected_revision':1})
        self.assertEqual(self.store.list(),[updated])

    def test_edit_supports_first_feature_records_without_revision(self):
        trip=self.store.create(self.data);del trip['revision']
        with self.store.connect() as connection:connection.execute('UPDATE trips SET snapshot=? WHERE id=?',(json.dumps(trip),trip['id']))
        updated=self.store.edit(trip['id'],{'title':'','notes':'','trip_date':None,'expected_revision':0})
        self.assertEqual(updated['title'],'A visit to Osaka');self.assertEqual(updated['notes'],'')
        self.assertIsNone(updated['trip_date']);self.assertEqual(updated['revision'],1)

    def test_failed_database_update_leaves_original_intact(self):
        trip=self.store.create(self.data)
        with self.store.connect() as connection:
            connection.execute("CREATE TRIGGER reject_edit BEFORE UPDATE ON trips BEGIN SELECT RAISE(ABORT, 'simulated storage failure'); END")
        import sqlite3
        with self.assertRaises(sqlite3.IntegrityError):self.store.edit(trip['id'],{'notes':'Do not commit','expected_revision':1})
        self.assertEqual(self.store.list(),[trip])
        self.assertTrue(self.store.photo_path(trip['photos'][0]['url']).is_file())

    def test_concurrent_edits_do_not_silently_overwrite(self):
        from concurrent.futures import ThreadPoolExecutor
        trip=self.store.create(self.data)
        def change(title):
            try:return self.store.edit(trip['id'],{'title':title,'expected_revision':1})
            except ConflictError:return 'conflict'
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(change,['A','B']))
        self.assertEqual(results.count('conflict'),1);self.assertEqual(len(self.store.list()),1)
        self.assertEqual(self.store.list()[0]['revision'],2)

    def test_delete_removes_only_target_and_its_photos(self):
        trip=self.store.create(self.data)
        self.data['request_id']=str(uuid4());other=self.store.create(self.data)
        target=self.store.photo_path(trip['photos'][0]['url']);other_photo=self.store.photo_path(other['photos'][0]['url'])
        result=self.store.remove(trip['id'],{'expected_revision':1})
        self.assertEqual(result,{'id':trip['id'],'deleted':True,'cleanup_pending':False})
        self.assertEqual(self.store.list(),[other]);self.assertFalse(target.exists());self.assertTrue(other_photo.exists())
        self.assertIsNone(self.store.photo_path(trip['photos'][0]['url']))
        self.assertEqual(AlbumStore(self.temp.name,self.cities).list(),[other])

    def test_delete_retry_and_create_replay_cannot_restore_trip(self):
        trip=self.store.create(self.data);result=self.store.remove(trip['id'],{'expected_revision':1})
        self.assertEqual(self.store.remove(trip['id'],{'expected_revision':1}),result)
        with self.assertRaises(ConflictError):self.store.create(self.data)
        with self.assertRaises(NotFoundError):self.store.edit(trip['id'],{'title':'restore','expected_revision':1})
        self.assertEqual(self.store.list(),[])
        with self.store.connect() as connection:self.assertEqual(connection.execute('SELECT snapshot FROM trips WHERE id=?',(trip['id'],)).fetchone()[0],'{}')

    def test_invalid_or_stale_delete_keeps_trip(self):
        trip=self.store.create(self.data)
        for data in [{},{'expected_revision':True},{'expected_revision':-1},{'expected_revision':1,'city_id':'jp-tokyo'},None]:
            with self.assertRaises(ValidationError):self.store.remove(trip['id'],data)
        with self.assertRaises(ConflictError):self.store.remove(trip['id'],{'expected_revision':0})
        with self.assertRaises(NotFoundError):self.store.remove(str(uuid4()),{'expected_revision':1})
        self.assertEqual(self.store.list(),[trip]);self.assertIsNotNone(self.store.photo_path(trip['photos'][0]['url']))

    def test_failed_delete_commit_keeps_record_and_photos(self):
        import sqlite3
        trip=self.store.create(self.data);photo=self.store.photo_path(trip['photos'][0]['url']);original=photo.read_bytes()
        with self.store.connect() as connection:connection.execute("CREATE TRIGGER reject_delete BEFORE UPDATE ON trips BEGIN SELECT RAISE(ABORT, 'simulated disk failure'); END")
        with self.assertRaises(sqlite3.IntegrityError):self.store.remove(trip['id'],{'expected_revision':1})
        self.assertEqual(self.store.list(),[trip]);self.assertEqual(photo.read_bytes(),original)

    def test_cleanup_failure_is_visible_and_deleted_media_stays_private(self):
        trip=self.store.create(self.data);photo=self.store.photo_path(trip['photos'][0]['url'])
        with patch('album_store.shutil.rmtree',side_effect=PermissionError('busy file')):
            self.assertTrue(self.store.remove(trip['id'],{'expected_revision':1})['cleanup_pending'])
            self.assertEqual(self.store.list(),[]);self.assertTrue(photo.exists())
            self.assertIsNone(self.store.photo_path(trip['photos'][0]['url']))
        self.assertEqual(self.store.list(),[]);self.assertFalse(photo.exists())

    def test_original_schema_migrates_without_losing_existing_trip(self):
        import sqlite3
        trip=self.store.create(self.data);del trip['revision']
        legacy=Path(self.temp.name)/'legacy';legacy.mkdir()
        with sqlite3.connect(legacy/'album.sqlite3') as connection:
            connection.execute('CREATE TABLE trips (id TEXT PRIMARY KEY, request_id TEXT UNIQUE, request_hash TEXT, snapshot TEXT)')
            connection.execute('INSERT INTO trips VALUES (?,?,?,?)',(trip['id'],str(uuid4()),'old-hash',json.dumps(trip)))
        store=AlbumStore(legacy,self.cities);self.assertEqual(store.list(),[trip]);store.remove(trip['id'],{'expected_revision':0});self.assertEqual(store.list(),[])


class HttpTests(unittest.TestCase):
    def setUp(self):
        AlbumTests.setUp(self)
        self.server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
        self.server.album=self.store
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base=f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();AlbumTests.tearDown(self)

    def test_http_create_and_media(self):
        request=Request(self.base+'/api/trips',json.dumps(self.data).encode(),headers={'Content-Type':'application/json','Origin':self.base})
        with urlopen(request) as response:
            self.assertEqual(response.status,201);trip=json.load(response)
        with urlopen(self.base+trip['photos'][0]['url']) as response:
            self.assertEqual(response.headers['Content-Type'],'image/jpeg')
        with urlopen(self.base+'/api/trips') as response:self.assertEqual(len(json.load(response)),1)
        with self.assertRaises(HTTPError) as error:urlopen(self.base+'/.local-album/album.sqlite3')
        self.assertEqual(error.exception.code,404)

    def test_cross_origin_and_invalid_uploads_rejected(self):
        for origin,body,content_type,status in [('https://example.com',b'{}','application/json',403),
                                              (self.base,b'{','application/json',400),
                                              (self.base,b'{}','text/plain',415)]:
            request=Request(self.base+'/api/trips',body,headers={'Content-Type':content_type,'Origin':origin})
            with self.assertRaises(HTTPError) as error:urlopen(request)
            self.assertEqual(error.exception.code,status)
        request=Request(self.base+'/api/trips',b'',headers={'Content-Type':'application/json','Content-Length':str(MAX_REQUEST_BYTES+1)})
        with self.assertRaises(HTTPError) as error:urlopen(request)
        self.assertEqual(error.exception.code,413)
        self.assertEqual(self.store.list(),[])

    def test_http_patch_validation_and_conflict(self):
        trip=self.store.create(self.data);url=self.base+'/api/trips/'+trip['id']
        def request(data,origin=None):
            return Request(url,json.dumps(data).encode(),method='PATCH',headers={'Content-Type':'application/json','Origin':origin or self.base})
        patch={'title':'Edited over HTTP','expected_revision':1}
        with urlopen(request(patch)) as response:self.assertEqual(json.load(response)['id'],trip['id'])
        for data,origin,status in [({'notes':'old','expected_revision':1},None,409),
                                   ({'city_id':'jp-tokyo','expected_revision':2},None,400),
                                   (patch,'https://example.com',403)]:
            with self.assertRaises(HTTPError) as error:urlopen(request(data,origin))
            self.assertEqual(error.exception.code,status)
        self.assertEqual(len(self.store.list()),1);self.assertEqual(self.store.list()[0]['title'],'Edited over HTTP')

    def test_http_delete_conflict_retry_and_missing_media(self):
        trip=self.store.create(self.data);url=self.base+'/api/trips/'+trip['id']
        def request(data,origin=None):return Request(url,json.dumps(data).encode(),method='DELETE',headers={'Content-Type':'application/json','Origin':origin or self.base})
        for data,origin,status in [({'expected_revision':0},None,409),({'expected_revision':True},None,400),({'expected_revision':1},'https://example.com',403)]:
            with self.assertRaises(HTTPError) as error:urlopen(request(data,origin))
            self.assertEqual(error.exception.code,status)
        for _ in range(2):
            with urlopen(request({'expected_revision':1})) as response:self.assertTrue(json.load(response)['deleted'])
        with self.assertRaises(HTTPError) as error:urlopen(self.base+trip['photos'][0]['url'])
        self.assertEqual(error.exception.code,404);self.assertEqual(self.store.list(),[])


if __name__=='__main__':unittest.main()
