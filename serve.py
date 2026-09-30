"""Local-only static preview. This is not Owen's trip API or a production server."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
    extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.geojson':'application/geo+json'}
    def do_GET(self):
        path=unquote(urlsplit(self.path).path)
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
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8019);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT)))
    print(f'Travel Memory Map: http://127.0.0.1:{args.port}/app/ (Ctrl+C to stop)',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
