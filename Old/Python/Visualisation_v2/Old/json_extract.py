import dpkt
import socket
import json
import optparse

def printPcap(pcap):
  res = [ { "connexion": []} ]
  for (ts, buf) in pcap:
    try:
      eth = dpkt.ethernet.Ethernet(buf)
      ip = eth.data
      src = socket.inet_ntoa(ip.src)
      dst = socket.inet_ntoa(ip.dst)
      tcp = ip.data
      dport = str(tcp.dport)
      sport = str(tcp.sport)
      res[0]["connexion"].append({ "IPSrc" : src, "IPDest" : dst,"PortSrc" : sport, "PortDest" : dport})
    except:
      pass
  sort = json.dumps(res, sort_keys=True, indent=4)
  print sort

def main():
  parser = optparse.OptionParser('Usage -> python json_extract.py -p <pcap file>')
  parser.add_option('-p', dest='pcapFile', type='string', help='specify pcap filename')
  (options,args) = parser.parse_args()
  if options.pcapFile == None:
    print parser.usage
    exit(0)
  pcapFile = options.pcapFile
  f = open(pcapFile)
  pcap = dpkt.pcap.Reader(f)
  printPcap(pcap)


if __name__ == "__main__":
  main()
