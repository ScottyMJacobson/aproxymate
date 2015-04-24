''' aproxymate: a simple proxy that handles GET requests for a particular URL,
 fetches that resource from the remote server, and returns it to the requester.

TODO Advanced features: 
    - use redis for caching
    - distributed proxy (multiple helper threads)
        - separate I/O threads
        - distributed caching
        - message & task queue
    -WSGI compatibility?
  '''

#! /usr/local/bin/python
# -*- coding: utf-8 -*-

# Scotty Jacobson

import argparse

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer   import ThreadingMixIn

import urllib2

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class AproxymateRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        all_headers = self.headers
        path_requested = self.path.lower()
        print "Request for {0}".format(path_requested)
        
        # check if exactly this request has been made before (send if true)
        cached_message = global_proxy.check_in_cache(path_requested)
        if cached_message:
            self.wfile.write(cached_message.headers)
            self.wfile.write(cached_message.message_data)
            return

        # tell remote server not to gzip or otherwise encode response 
        all_headers['accept-encoding'] = 'identity'
        # run this GET request on the path requested, with same headers
        request_out = urllib2.Request(path_requested, headers = all_headers)
        try:
            response_back = urllib2.urlopen(request_out)
        except urllib2.HTTPError as e:
            self.send_error(e.code, e.message)
            return
        except urllib2.URLError as e:
            self.send_error(404)
            return

        response_code_back = response_back.getcode()
        headers_back = response_back.info()
        data_back = response_back.read()

        lines_in_header = []
        lines_in_header.append("HTTP 1.1 {0} {1}".format(response_code_back, BaseHTTPRequestHandler.responses[response_code_back][0]))

        for header in response_back.headers:
            lines_in_header.append("{0}: {1}".format(header, response_back.headers[header]))

        #symbolize end of headers
        lines_in_header.append('')
        lines_in_header.append('')

        headers = '\n'.join(lines_in_header)
        self.wfile.write(headers)
        self.wfile.write(data_back)
        global_proxy.place_in_cache(path_requested, CacheEntry(headers, data_back))


class CacheEntry():
    def __init__(self, headers, message_data):
        self.headers = headers
        self.message_data = message_data


class Aproxymate():
    def __init__(self):
        self.port = None
        #for now a cache is just a key value store of paths to response messages
        self.cache = {}

    def listen(self, port):
        self.port = port
        try:
            self.server = ThreadedHTTPServer(("", port), AproxymateRequestHandler)
            print "Threaded, caching proxy server listening on port", self.port
            self.server.serve_forever() 
        except KeyboardInterrupt:
            print " KeyboardInterrupt received. Shutting down server."

    def place_in_cache(self, path_requested, cache_entry):
        print "Placing path", path_requested, "in cache."
        self.cache[path_requested] = cache_entry
        return True

    def check_in_cache(self, path_requested):
        if path_requested in self.cache:
            print "Found cache entry for", path_requested
            return self.cache[path_requested]
        else:
            print "No cache entry for", path_requested
            return None

global_proxy = Aproxymate()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int ,help="Port number to bind proxy to")
    args = parser.parse_args()

    global_proxy.listen(args.port)

if __name__ == '__main__':
    main()
