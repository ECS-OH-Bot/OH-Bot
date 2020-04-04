# Python script to respond to http requests on port 8000
# This is to stop azure web services from thinking that the application has crashed and restarting it
# This should be integrated with the main program at some point so that azure will actually restard a crashed app.

import http.server
import socketserver
from http import HTTPStatus


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        self.wfile.write(b'Hello world')


httpd = socketserver.TCPServer(('', 8000), Handler)
httpd.serve_forever()
