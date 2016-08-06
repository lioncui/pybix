#!/usr/bin/python
# -*- coding: utf-8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import json
import cgi


class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        self.send_response(200)
        self.end_headers()
        #parameters = {}
        #result = {}
        # for p in parsed_path.query.split("&"):
        #    parameters[p.split("=")[0]] = p.split("=")[1]
        result = {
            'tasks': {
                '11722': {
                    'agentType': "server",
                    'pluginClassName': "ServerPlugin",
                    'pluginFileName': "ServerPlugin",
                    'status': "1",
                    "taskConf": {
                        "type": ["cpu", "mem", "diskio", "diskstore", "netio", "procsum"],
                        "pluginTime": 30
                    },
                    'uuid': "11722"
                }
            }
        }
        self.wfile.write(json.dumps(result))
        return result

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        print(form['post_data'])

        self.send_response(200)
        self.end_headers()
        result = {
            'agent': {
                'agentTime': 20,
                'post_time': 30,
            },
        }
        self.wfile.write(json.dumps(result))

        return

if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    print('...')
    server = HTTPServer(('0.0.0.0', 8010), GetHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()
