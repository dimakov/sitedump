import urllib
import sys
import time
import logging


def proxylistcheck(listofproxies, times):

    """logging stuff"""
    log = logging.getLogger('')
    #log.setLevel(logging.INFO)

    if not listofproxies:
        print "Please supply file with proxies"
        sys.exit(1)
    try:
        proxies = open(listofproxies, "r")
    except IOError:
        log.error("Error: File does not appear to exist.")
        sys.exit(1)
    good = proxies.read().splitlines()
    for i in xrange(times):
        log.info("New iteration")
        for proxy in good:
            httpprox = "http://" + str(proxy)
            begin = time.time()
            try:
                urllib.urlopen("http://www.google.com", proxies={'http': httpprox})
            except IOError:
                log.info("Proxy %s is dead." % httpprox)
                good.remove(proxy)
            else:
                end = time.time()
                if end - begin > 1.5:
                    log.info("Proxy %s to slow, took %.5f seconds." % (httpprox, end - begin))
                    good.remove(proxy)
                    continue
                log.info("Proxy %s is OK" % httpprox)

    proxies.close()

    log.info("Finished analyzid list")

    return good

if __name__ == "__main__":
    goodlist = proxylistcheck(sys.argv[1], 5)
    try:
        goodl = open('goodlist.txt', "w")
    except IOError:
        log.error("Error: Couldn`t create output file.")
        sys.exit(1)

    for item in goodlist:
        goodl.write(item + "\n")

    goodl.close()
    sys.exit(0)

