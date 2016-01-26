# Network Visualization for Penetration Testing

import options
import parser2
import time
import socket
import optparse
import json
import os

  

def main():
    ti = time.clock()
    pcapFile = options.getargs()
    res = parser2.parse(pcapFile)
    if res.has_key("Error"):
        print "Parsing canceled, an error has occured"
    t1 = time.clock() - ti
    print "----------------------"
    print "Parsing time :" + str(t1)
    with open('dev/trame.json', 'w') as outfile:
        json.dump(res["trames"], outfile)
    #print res["trames"][0:15]
    with open('dev/session.json', 'w') as outfile:
        json.dump(res["sessions"], outfile)
    with open('dev/user.json', 'w') as outfile:
        json.dump(res["user"], outfile)
    print "----------------------"
    print "Writing time : " + str(time.clock() - t1)        
    print "Total time : " + str(time.clock() - ti)
   #json.dumps(res[0]["trames"])
    #print json2


if __name__ == "__main__":
    main()
