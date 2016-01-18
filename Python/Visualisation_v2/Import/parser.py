from scapy.all import *
from datetime import datetime
import json

def parse(filename):
    """
    Parses pcap file into sqlite database
    """
    pcap = rdpcap(filename)
    res = [ { "connexion": []} ]
    counts = { "total":0, "ip":0, "tcp":0, "udp":0, "icmp":0, "arp":0 }
    
    for pkt in pcap:
        counts["total"] += 1
       
        packet = {}
        packet['ts'] = datetime.fromtimestamp(pkt.time).strftime('%Y-%m-%d %H:%M:%S')
        
        if pkt.haslayer(IP):
            counts["ip"] += 1
            ip = pkt.getlayer(IP) 
            packet['id'] = ip.id
            
            if ip.haslayer(TCP):
                counts["tcp"] += 1
                tcp = ip.getlayer(TCP)
                packet["proto"] = "tcp"
                packet["src"] = ( ip.src, tcp.sport )
                packet["dst"] = ( ip.dst, tcp.dport )
                
            elif ip.haslayer(UDP):
                counts["udp"] += 1
                udp = ip.getlayer(UDP)
                packet["proto"] = "udp"
                packet["src"] = ( ip.src, udp.sport )
                packet["dst"] = ( ip.dst, udp.dport )
                
            elif ip.haslayer(ICMP):
                counts["icmp"] += 1
                icmp = ip.getlayer(ICMP)
                packet["proto"] = "icmp"
                packet["src"] = ( ip.src, None )
                packet["dst"] = ( ip.dst, None )
                
            else:
                #pkt.show()
                continue
                
        elif pkt.haslayer(ARP):
            counts["arp"] += 1 
            arp = pkt.getlayer(ARP)
            
            packet["proto"] = "arp"
            packet["id"] = None
            packet["src"] = ( arp.psrc , None )
            packet["dst"] = ( arp.pdst, None )  
              
        else:
            #pkt.show()
            continue
            
        #print "\tprocessing pkt w/ timestamp %s, %s -> %s..." % ( packet["ts"], packet["src"][0], packet["dst"][0] )
        #database.insert_packet(packet)
        #res[0]["connexion"].append(packet)
        res[0]["connexion"].append({ "IPSrc" : packet["src"][0], "IPDest" : packet["dst"][0] ,"Protocole" : packet["proto"]})

    returnjson =  json.dumps(res, sort_keys=True)
    print "Done parsing, here are some statistics: "
    print "\t", counts
    
    return res