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
    with open('data.json', 'w') as outfile:
        json.dump(res, outfile)
    json.dumps(res)
    #print json2


if __name__ == "__main__":
    main()
