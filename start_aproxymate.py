import argparse
import sys
from os import path

import threading
import time

from aproxymate import aproxymate

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("proxy_port", type=int ,help="Port number to bind proxy to")
    parser.add_argument("memkeshed_port", type=int ,help="Port number memkeshed is listening on")
    args = parser.parse_args()


    proxy_instance = aproxymate.AproxymateServer(args.proxy_port, args.memkeshed_port)  
    proxy_daemon = threading.Thread(target=proxy_instance.listen)
    proxy_daemon.setDaemon(True)
    proxy_daemon.start()

    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()