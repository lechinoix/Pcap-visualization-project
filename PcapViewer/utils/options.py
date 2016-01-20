import optparse
import os

def getargs():   
    parser = optparse.OptionParser('Usage -> python main.py -p <pcap file>')
    parser.add_option('-p', dest='pcapFile', type='string', help='specify pcap filename')
    (options,args) = parser.parse_args()
    
    if options.pcapFile == None:
        print parser.usage
        exit(0)
    
    args = options.pcapFile
    
    # TO DO : Check que le pcap est valide


    
    return args