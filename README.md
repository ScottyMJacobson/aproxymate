# aproxymate
**It's a proxy, mate**

**v. 0.1.0**

Aproxymate is a fairly simple HTTP proxy written in python that handles 
HTTP GET requests and does basic persistent caching. 

## Usage:

In the root directory, run the command `python aproxymate/aproxymate.py [port]`

## Future Improvements: 
I hope to get to a few, if not all, of these improvements by the time the final
project is due:

- Port the caching mechanism to Memcache, or (preferably) Redis to enable
persistant caching (or implement it myself)
- Make the caching mechanism cache-header-aware, and either follow those
directions or have its own invalidation scheme for how long to cache a result
- Have a number of helper threads to distribute the I/O load
- Create a full-on message and task queue to completely decouple: request,
checking the cache/requesting from the destination server, and responding
to the client


## Limitations:
As of version 0.1.0, the following limitations are explicitly in place 
(others may be implicit):

- The destination server is notified not to use gzip or any other 
compression encoding schemes (the binary stream was getting garbled) and instead
use `identity` encoding 
- The proxy only accepts HTTP GET requests
- Upon shutdown, the proxy's cache is emptied as it is stored in memory
and does not serialize
- Unable to handle 301 and other redirect / more complex response codes



