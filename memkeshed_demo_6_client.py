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

    mk_client = memkeshed.MemKeshedClient(args.memkeshed_port)


    print "Putting value 'the_test_value' for key 'test_key': \n", mk_client.put_key("test_key", "the_test_value", 1000)
    time.sleep(2)
    print "Getting value for key 'test_key':\n", mk_client.get_key("test_key")

if __name__ == "__main__":
    main()
