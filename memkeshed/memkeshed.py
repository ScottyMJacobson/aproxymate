''' memkeshed: a dumbed-down version of memcache implemented in python
'''
import threading
import select
import socket
import sys
import Queue
import SocketServer
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    )

BUFFER_SIZE = 1024

def recv_until_delineator(recv_function, delineator):
    last_char = ''
    retval = ""
    while last_char != delineator:
        last_char = recv_function(1)
        retval += last_char
    return retval[:-1]

class MemKeshedClient():
    def __init__(self, port):
        self.port = port

    def put_key(self, key, value, time_to_cache):
        # send memkeshed message to server
        # format: tiktokz key time_to_cache data_length 
        data_length = len(value)
        request_text = "tiktokz {0} {1} {2}\n{3}\n".format(key, time_to_cache, data_length, value)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', self.port))
        s.send(request_text)
        raw_response = s.recv(BUFFER_SIZE)
        s.close()
        if raw_response == PUT_KEY_SUCCESS:
            return PUT_KEY_SUCCESS
        if raw_response == PUT_KEY_ERROR:
            return None


    def get_key(self, key):
        request_text = "rwhower {0}".format(key)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', self.port))
        s.send(request_text)
        response_status = recv_until_delineator(s.recv, " ")

        s.close()

        # send memkeshed message to server
        # parse response for value
        # return value
        pass


SUPPORTED_COMMANDS = ['tiktokz', 'rwhower']

PUT_KEY_COMMAND = "tiktokz"
PUT_KEY_SUCCESS = "$$$$$$$"
PUT_KEY_ERROR = "dbstopd"

GET_KEY_COMMAND = "rwhower"
GET_KEY_SUCCESS = "sprstrz"
GET_KEY_ERROR = "dbblown"


'''A subclass of SocketServer RequestHandlers, this contains the 
logic for how to handle and execute memkeshed commands '''
# inspired by http://pymotw.com/2/SocketServer/
class MemKeshedRequestHandler(SocketServer.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('MemKeshedRequestHandler')
        self.logger.debug('__init__')
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self):
        self.logger.debug('setup')
        return SocketServer.BaseRequestHandler.setup(self)

    def handle(self):
        self.logger.debug('handle')

        # Echo the back to the client
        command = self.recv_until_delineator(self.request.recv, ' ')
            
        if not command in SUPPORTED_COMMANDS:
            return self.respond_with_error("Command Unrecognized")

        return self.respond_by_command(command)

    def respond_by_command(self, command_txt):
        self.logger.debug('Responding to command {0}'.format(command_txt))

        if command_txt == PUT_KEY_COMMAND:
            key = self.recv_until_delineator(self.request.recv, ' ')
            self.logger.debug('key is {0}'.format(key))
            time_to_cache = int(self.recv_until_delineator(self.request.recv, ' '))
            self.logger.debug('time_to_cache is {0}'.format(time_to_cache))
            data_length = int(self.recv_until_delineator(self.request.recv, '\n'))
            self.logger.debug('data_length is {0}'.format(data_length))
            data_value = self.request.recv(data_length)
            self.logger.debug('data payload is {0}'.format(data_value))
            if self.server.put_key(key, data_value, time_to_cache):
                self.request.send(PUT_KEY_SUCCESS)
            else:
                self.request.send(PUT_KEY_ERROR)

        elif command_txt == GET_KEY_COMMAND:
            key = self.recv_until_delineator(self.request.recv, ' ')
            self.logger.debug('key is {0}'.format(key))
            value_from_database = self.server.get_key(key)
            self.send_lookup_result(value_from_database)

    def send_lookup_result(self, value_from_database):
        if value_from_database:
            payload = " ".join([GET_KEY_SUCCESS, len(value_from_database, value_from_database)])
            self.request.send(payload)
        else:
            self.request.send(GET_KEY_ERROR+" \n")


    def respond_with_error(self, error_msg):
        self.logger.debug('Sending error')
        self.request.send("errorzz ERROR: "+error_msg+"\n");
        return

    def finish(self):
        self.logger.debug('finish')
        return SocketServer.BaseRequestHandler.finish(self)



class MemKeshedDataInstance():
    def __init__(self, value):
        self.value = value

class MemKeshedDatabase():
    def __init__(self):
        self.store = {}
        self.global_store_lock = threading.RLock()

    def put_key(self, key, value, time_to_cache):
        with self.global_store_lock:
            self.store[key] = MemKeshedDataInstance(value)
        return True

    def get_key(self, key):
        retval = None
        with self.global_store_lock:
            if key in self.store:
                retval = self.store[key]
        return retval


'''A subclass of SocketServer.TCPServer, MemKeshedServer loads a database and hands
its requests to the handler MemKeshedRequestHandler unless otherwise specified'''
# inspired by http://pymotw.com/2/SocketServer/
class MemKeshedServer(SocketServer.TCPServer):
    def __init__(self, server_address, handler_class=MemKeshedRequestHandler):
        self.database = MemKeshedDatabase()
        self.logger = logging.getLogger('MemKeshedServer')
        self.logger.debug('__init__')
        SocketServer.TCPServer.__init__(self, server_address, handler_class)
        return

    def put_key(self, *args):
        return self.database.put_key(*args)

    def get_key(self, *args):
        return self.database.get_key(*args)

    def server_activate(self):
        self.logger.debug('server_activate')
        SocketServer.TCPServer.server_activate(self)
        return

    def serve_forever(self):
        self.logger.debug('waiting for request')
        self.logger.info('Handling requests, press <Ctrl-C> to quit')
        while True:
            self.handle_request()
        return

    def handle_request(self):
        self.logger.debug('handle_request')
        return SocketServer.TCPServer.handle_request(self)

    def verify_request(self, request, client_address):
        self.logger.debug('verify_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        self.logger.debug('process_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.process_request(self, request, client_address)

    def server_close(self):
        self.logger.debug('server_close')
        return SocketServer.TCPServer.server_close(self)

    def finish_request(self, request, client_address):
        self.logger.debug('finish_request(%s, %s)', request, client_address)
        return SocketServer.TCPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        self.logger.debug('close_request(%s)', request_address)
        return SocketServer.TCPServer.close_request(self, request_address)





