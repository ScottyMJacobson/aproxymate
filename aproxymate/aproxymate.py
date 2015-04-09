''' aproxymate: a simple proxy that handles GET requests for a particular URL,
 fetches that resource from the remote server, and returns it to the requester.

Advanced features: 
    - caching
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

class Aproxymate():
    def __init__(self, portno):
        self.port = portno



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=str ,help="Port number to bind proxy to")
    args = parser.parse_args()

    proxy = Aproxymate(args.port)


if __name__ == '__main__':
    main()