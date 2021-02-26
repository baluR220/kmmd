from http.server import *
import os
import time
import json
import sys


work_dir = os.path.dirname(os.path.realpath(__file__))
path_to_pl = os.path.join(work_dir, 'clients', 'playlist')
path_to_log = os.path.join(work_dir, 'log', 'log')


class CustomHandler(BaseHTTPRequestHandler):

    def set_headers(self):
        self.send_response(200)
        time_stamp = time.ctime(os.path.getmtime(path_to_pl))
        self.send_header('Content-type', 'text/html')
        self.send_header('Last-Modified', time_stamp)
        self.end_headers()

    def do_GET(self):
        self.set_headers()
        pl = []
        with open(path_to_pl) as out:
            for line in out:
                pl.append(line.strip())
        out = json.dumps(pl).encode('utf-8')
        self.wfile.write(out)

    def do_HEAD(self):
        self.set_headers()


def start_server(server_class=HTTPServer, handler_class=CustomHandler):
    server_address = ('', 80)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    with open(path_to_log, 'w') as log:
        # sys.stdout = log
        # sys.stderr = log
        print('starting server')
        start_server()
