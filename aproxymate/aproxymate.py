''' aproxymate: a simple proxy that handles GET requests for a particular URL,
checks with a MemKe$hed server if it is in its cache, and either returns the 
cached value, or fetches the resource from the remote server, caches it using 
memkeshed and returns it to the requester.

'''

#! /usr/local/bin/python
# -*- coding: utf-8 -*-

# Scotty Jacobson

import argparse
import sys
from os import path

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer   import ThreadingMixIn

from memkeshed import memkeshed

import json

import urllib2

CACHE_TIME = 5

class AproxymateRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        all_headers = self.headers
        path_requested = self.path.lower()
        print "Request for {0}".format(path_requested)
        
        # check if exactly this request has been made before (send if true)
        cached_message = self.server.check_in_cache(path_requested)
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
        self.server.place_in_cache(path_requested, CacheEntry(headers, data_back), CACHE_TIME)


class CacheEntry():
    def __init__(self, headers, message_data):
        self.headers = headers
        self.message_data = message_data

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class AproxymateMemKeshedClient(memkeshed.MemKeshedClient):
    def put_key(self, key, cache_entry, time_to_cache):
        entry_dict = {'headers':cache_entry.headers, 'message_data': cache_entry.message_data}
        serialized_entry = json.dumps(entry_dict)
        super(AproxymateMemKeshedClient, self).put_key(key, serialized_entry, time_to_cache)

    def get_key(self, key):
        serialized_entry = super(AproxymateMemKeshedClient, self).get_key(key)
        if serialized_entry:
            entry_dict = json.loads(serialized_entry)
            entry_object = CacheEntry(entry_dict['headers'], entry_dict['message_data'])
            return entry_object
        else:
            return None 

class AproxymateServer(ThreadedHTTPServer):
    def __init__(self, proxy_port, memkeshed_port):
        self.proxy_port = proxy_port
        self.memkeshed_port = memkeshed_port
        self.memkeshed_client = AproxymateMemKeshedClient(memkeshed_port)
        ThreadedHTTPServer.__init__(self, ("127.0.0.1", proxy_port), AproxymateRequestHandler)
        return

    def listen(self):
        try:
            print "Threaded, caching (through MemKeshed) proxy server listening on port", self.proxy_port
            self.serve_forever() 
        except KeyboardInterrupt:
            print " KeyboardInterrupt received. Shutting down server."

    def place_in_cache(self, path_requested, cache_entry, time_to_cache):
        print "Placing path", path_requested, "in cache."
        return self.memkeshed_client.put_key(path_requested, cache_entry, time_to_cache)

    def check_in_cache(self, path_requested):
        value_from_mk = self.memkeshed_client.get_key(path_requested)
        if value_from_mk:    
            print "Found cache entry for", path_requested
            return value_from_mk
        else:
            print "No cache entry for", path_requested
            return None



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("proxy_port", type=int ,help="Port number to bind proxy to")
    parser.add_argument("memkeshed_port", type=int ,help="Port number memkeshed is listening on")
    args = parser.parse_args()

    proxy_instance = AproxymateServer(args.proxy_port, args.memkeshed_port)  
    proxy_instance.listen()


if __name__ == '__main__':
    main()
