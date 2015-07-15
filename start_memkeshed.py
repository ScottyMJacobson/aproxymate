'''
A script with a main that lunches up an instance of a memkeshed daemon
'''
import argparse
import threading

import time

from memkeshed import memkeshed 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("memkeshed_port", type=int ,help="Port number to bind proxy to")
    args = parser.parse_args()

    address_struct = ("127.0.0.1", args.memkeshed_port)
    mk_server = memkeshed.MemKeshedServer(address_struct)
    mk_daemon = threading.Thread(target=mk_server.serve_forever)
    mk_daemon.setDaemon(True)
    mk_daemon.start()

    #Hack to allow ctrl-C to close the daemon
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
