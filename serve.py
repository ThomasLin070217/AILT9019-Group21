"""Local-only demo preview. The real local backend is ``python3 -m backend``."""
import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from map_config import read_map_config

ROOT = Path(__file__).resolve().parent

def map_config():
    """Only publish browser Maps settings, never arbitrary environment values."""
    return read_map_config(ROOT)

class Handler(SimpleHTTPRequestHandler):
    extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.geojson':'application/geo+json'}
    def do_GET(self):
        path=unquote(urlsplit(self.path).path)
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
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-eval' https://*.googleapis.com https://*.gstatic.com blob:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: blob: https://*.googleapis.com https://*.gstatic.com https://*.google.com https://*.googleusercontent.com https://tiles.openfreemap.org; connect-src 'self' https://*.googleapis.com https://*.gstatic.com https://*.google.com https://tiles.openfreemap.org data: blob:; font-src 'self' https://fonts.gstatic.com https://tiles.openfreemap.org; worker-src blob:; frame-src https://*.google.com; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8019);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT)))
    print(f'Travel Memory Map: http://127.0.0.1:{args.port}/app/ (Ctrl+C to stop)',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
