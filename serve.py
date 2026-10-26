"""Local preview and album server, bound to loopback only."""
import argparse
import json
import os
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
from album_store import AlbumStore, ValidationError, ConflictError, NotFoundError, MAX_REQUEST_BYTES
from album_backup import AlbumBackup, MAX_BACKUP_BYTES
from ai_memory import AIError, public_settings, generate

ROOT = Path(__file__).resolve().parent

def map_config():
    """Only publish browser Maps settings, never arbitrary environment values."""
    values = {}
    config = ROOT / '.env.maps.local'
    if config.exists():
        for line in config.read_text().splitlines():
            name, separator, value = line.partition('=')
            if separator and name.strip() in ('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_MAP_ID'):
                values[name.strip()] = value.strip().strip('\"\'')
    key = os.environ.get('GOOGLE_MAPS_API_KEY', values.get('GOOGLE_MAPS_API_KEY', ''))
    return {'apiKey': key, 'mapId': os.environ.get('GOOGLE_MAPS_MAP_ID', values.get('GOOGLE_MAPS_MAP_ID', 'DEMO_MAP_ID')) or 'DEMO_MAP_ID'}

class Handler(SimpleHTTPRequestHandler):
    extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.geojson':'application/geo+json'}
    def trusted_request(self):
        allowed={f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        origin=self.headers.get('Origin')
        return self.headers.get('Host') in allowed and (not origin or origin in {f'http://{host}' for host in allowed})
    def send_json(self, value, status=200):
        body=json.dumps(value).encode()
        self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def send_download(self, body, mime, filename):
        self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(body)));self.send_header('Content-Disposition',f'attachment; filename="{filename}"');self.end_headers();self.wfile.write(body)
    def read_body(self, limit):
        length=int(self.headers.get('Content-Length','0'))
        if not 0 < length <= limit:raise ValidationError('Request is empty or exceeds the allowed size.')
        return self.rfile.read(length)
    def do_POST(self):
        if not self.trusted_request():
            self.send_error(403);return
        path=urlsplit(self.path).path
        if path in {'/api/backups/preview','/api/backups/restore'}:
            self.handle_backup(path);return
        match=re.fullmatch(r'/api/trips/([0-9a-f-]{36})/generate',path)
        if match:
            self.handle_generate(match[1]);return
        match=re.fullmatch(r'/api/trips/([0-9a-f-]{36})/photos',path)
        if match:
            try:
                if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':raise ValidationError('Send application/json.')
                result=self.server.album.replace_photos(match[1],json.loads(self.read_body(MAX_REQUEST_BYTES)))
                self.send_json(result)
            except ConflictError as error:self.send_json({'error':str(error)},409)
            except NotFoundError as error:self.send_json({'error':str(error)},404)
            except (ValidationError,ValueError) as error:self.send_json({'error':str(error)},400)
            except Exception:self.send_json({'error':'Could not replace photos. Your saved trip is unchanged; keep the selected files and retry.'},500)
            return
        if urlsplit(self.path).path!='/api/trips':
            self.send_error(404);return
        if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':
            self.send_json({'error':'Send application/json.'},415);return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0 < length <= MAX_REQUEST_BYTES:
                self.send_json({'error':'Upload exceeds the request limit. Use photos up to 20 MB in total.'},413);return
            data=json.loads(self.rfile.read(length))
            self.send_json(self.server.album.create(data),201)
        except ConflictError as error:
            self.send_json({'error':str(error)},409)
        except (ValidationError, ValueError, UnicodeDecodeError) as error:
            self.send_json({'error':str(error)},400)
        except Exception as error:
            # Do not expose local paths or database internals to the browser.
            message=str(error) if isinstance(error,RuntimeError) else 'Could not save this trip. Keep the form open and retry; your inputs are still here.'
            self.send_json({'error':message},500)
    def handle_backup(self,path):
        if self.headers.get('Content-Type','').split(';')[0].strip()!='application/zip':
            self.send_json({'error':'Choose an album ZIP backup.'},415);return
        try:
            raw=self.read_body(MAX_BACKUP_BYTES);backup=AlbumBackup(self.server.album)
            if path.endswith('/preview'):self.send_json(backup.preview(raw))
            else:self.send_json(backup.restore(raw,copies=urlsplit(self.path).query=='copies=1'))
        except ConflictError as error:self.send_json({'error':str(error)},409)
        except (ValidationError,ValueError) as error:self.send_json({'error':str(error)},400)
        except Exception:self.send_json({'error':'Backup operation failed. Existing records were not overwritten. Check local storage and retry.'},500)
    def handle_generate(self,trip_id):
        if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':
            self.send_json({'error':'Send application/json.'},415);return
        try:
            data=json.loads(self.read_body(16*1024))
            if not isinstance(data,dict) or set(data)!={'expected_revision','consent'} or data.get('consent') is not True or type(data.get('expected_revision')) is not int:
                raise ValidationError('Generation requires explicit consent and the reviewed trip revision.')
            trip=self.server.album.get(trip_id)
            if trip.get('revision',0)!=data['expected_revision']:raise ConflictError('The trip changed. Refresh and review what will be sent before generating.')
            result=generate(ROOT,self.server.album,trip)
            if self.server.album.get(trip_id).get('revision',0)!=data['expected_revision']:raise ConflictError('The trip changed during generation. Your saved record is unchanged by AI; review it before retrying.')
            self.send_json(result)
        except AIError as error:self.send_json({'error':str(error)},error.status)
        except NotFoundError as error:self.send_json({'error':str(error)},404)
        except ConflictError as error:self.send_json({'error':str(error)},409)
        except (ValidationError,ValueError) as error:self.send_json({'error':str(error)},400)
        except Exception:self.send_json({'error':'AI generation failed. Your saved trip is unchanged. Check the local setup and retry manually.'},502)
    def serve_media(self, path, head=False):
        if not self.trusted_request():
            self.send_error(403);return
        target=self.server.album.photo_path(path)
        if target is None:
            self.send_error(404);return
        try:body=target.read_bytes()
        except FileNotFoundError:
            self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type','image/jpeg');self.send_header('Content-Length',str(len(body)));self.end_headers()
        if not head:self.wfile.write(body)
    def do_PATCH(self):
        self.write_trip('edit')
    def do_DELETE(self):
        self.write_trip('remove')
    def write_trip(self, operation):
        if not self.trusted_request():
            self.send_error(403);return
        match=re.fullmatch(r'/api/trips/([0-9a-f-]{36})',urlsplit(self.path).path)
        if not match:
            self.send_error(404);return
        if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json':
            self.send_json({'error':'Send application/json.'},415);return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0 < length <= 64*1024:
                self.send_json({'error':'Trip edits must be at most 64 KB.'},413);return
            data=json.loads(self.rfile.read(length))
            self.send_json(getattr(self.server.album,operation)(match[1],data))
        except NotFoundError as error:
            self.send_json({'error':str(error)},404)
        except ConflictError as error:
            self.send_json({'error':str(error)},409)
        except (ValidationError, ValueError, UnicodeDecodeError) as error:
            self.send_json({'error':str(error)},400)
        except Exception:
            message='Could not delete this trip. Its saved record and photos are unchanged. Retry when local storage is available.' if operation=='remove' else 'Could not save these changes. Your saved trip is unchanged; keep the editor open and retry.'
            self.send_json({'error':message},500)
    def do_GET(self):
        path=unquote(urlsplit(self.path).path)
        if path in {'/api/backup','/api/ai-config'}:
            if not self.trusted_request():self.send_error(403);return
            try:
                if path=='/api/backup':self.send_download(AlbumBackup(self.server.album).export(),'application/zip','travel-memory-backup.zip')
                else:self.send_json(public_settings(ROOT))
            except AIError as error:self.send_json({'error':str(error)},error.status)
            except ValidationError as error:self.send_json({'error':str(error)},400)
            except Exception:self.send_json({'error':'Could not read the local configuration or album files. Check local storage.'},500)
            return
        if path in {'/api/cities','/api/trips'}:
            if not self.trusted_request():
                self.send_error(403);return
            try:self.send_json(list(self.server.album.cities.values()) if path=='/api/cities' else self.server.album.list())
            except Exception:self.send_json({'error':'Could not read the local album. Check that its storage folder is available.'},500)
            return
        if path.startswith('/media/'):
            self.serve_media(path);return
        if path=='/api/map-config':
            allowed_hosts={f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            origin=self.headers.get('Origin')
            if self.headers.get('Host') not in allowed_hosts or (origin and urlsplit(origin).netloc not in allowed_hosts):
                self.send_error(403);return
            body=json.dumps(map_config()).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
        if path=='/':
            self.send_response(302);self.send_header('Location','/app/');self.end_headers();return
        target=(ROOT/path.lstrip('/')).resolve()
        allowed=any(target.is_relative_to(ROOT/folder) for folder in ['app','data'])
        if not allowed or any(part.startswith('.') for part in Path(path).parts):
            self.send_error(404);return
        super().do_GET()
    def do_HEAD(self):
        path=unquote(urlsplit(self.path).path)
        if path.startswith('/media/'):
            self.serve_media(path,head=True);return
        target=(ROOT/path.lstrip('/')).resolve()
        if not any(target.is_relative_to(ROOT/folder) for folder in ['app','data']) or any(part.startswith('.') for part in Path(path).parts):
            self.send_error(404);return
        super().do_HEAD()
    def list_directory(self,path):
        self.send_error(404);return None
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-eval' https://*.googleapis.com https://*.gstatic.com blob:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: blob: https://*.googleapis.com https://*.gstatic.com https://*.google.com https://*.googleusercontent.com; connect-src 'self' https://*.googleapis.com https://*.gstatic.com https://*.google.com data: blob:; font-src 'self' https://fonts.gstatic.com; worker-src blob:; frame-src https://*.google.com; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8019)
    parser.add_argument('--data-dir',type=Path,default=ROOT/'.local-album',help='Private local album directory (default: .local-album)')
    args=parser.parse_args()
    if any(args.data_dir.resolve().is_relative_to((ROOT/folder).resolve()) for folder in ['app','data']):
        parser.error('Choose a private --data-dir outside app/ and data/.')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT)))
    server.album=AlbumStore(args.data_dir,json.loads((ROOT/'data/cities.json').read_text()))
    print(f'Travel Memory Map: http://127.0.0.1:{server.server_port}/app/ (Ctrl+C to stop)',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
