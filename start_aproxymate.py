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
    parser.add_argument("-c", "--cache_secs", type=int,
                        help="Number of seconds to cache data for")
    args = parser.parse_args()

    if args.cache_secs:
        proxy_instance = aproxymate.AproxymateServer(args.proxy_port, args.memkeshed_port, args.cache_secs)  
    else:
        proxy_instance = aproxymate.AproxymateServer(args.proxy_port, args.memkeshed_port)  

    proxy_daemon = threading.Thread(target=proxy_instance.listen)
    proxy_daemon.setDaemon(True)
    proxy_daemon.start()

    #Hack to allow ctrl-C to close the daemon
    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()