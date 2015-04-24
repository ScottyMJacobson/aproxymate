'''
A script with a main that lunches up an instance of a memkeshed daemon
'''
import argparse
import threading

import time

from memkeshed import memkeshed 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int ,help="Port number to bind proxy to")
    args = parser.parse_args()

    address_struct = ("127.0.0.1", args.port)
    mk_server = memkeshed.MemKeshedServer(address_struct)
    mk_daemon = threading.Thread(target=mk_server.serve_forever)
    mk_daemon.setDaemon(True)
    mk_daemon.start()

    mk_client = memkeshed.MemKeshedClient(args.port)

    while True:
        print mk_client.put_key("test_key", "the_test_value", 1000)
        print mk_client.get_key("test_key")
        time.sleep(10)


if __name__ == "__main__":
    main()
