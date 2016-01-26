# Network Visualization for Penetration Testing

from Import import options
from Import import parser
import socket
import optparse
import json
import os

  

def main():
    
    pcapFile = options.getargs()
    res = parser.parse(pcapFile)
    with open('trame.json', 'w') as outfile:
        json.dump(res[0]["trames"], outfile)
    with open('session.json', 'w') as outfile:
        json.dump(res[0]["sessions"], outfile)
   #json.dumps(res[0]["trames"])
    #print json2


if __name__ == "__main__":
    main()
