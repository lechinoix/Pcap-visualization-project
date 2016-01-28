# Network Visualization for Penetration Testing

import options
import parser
import time
import socket
import optparse
import json
import os

  

def main():
    ti = time.clock()
    pcapFile = options.getargs()
    res = parser.parse(pcapFile)
    if res.has_key("Error"):
        print "Parsing canceled, an error has occured"
    t1 = time.clock() - ti
    print "----------------------"        
    print "Total time : " + str(t1)


if __name__ == "__main__":
    main()
