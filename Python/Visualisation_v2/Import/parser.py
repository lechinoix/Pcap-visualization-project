from scapy.all import *
from datetime import datetime
import json

def parse(filename):
    """
    Parses pcap file into sqlite database
    """
    pcap = rdpcap(filename)
    resultat=[{"trames":[],"sessions":[]}]
    counts = { "total":0, "ip":0, "tcp":0, "udp":0, "icmp":0, "arp":0 }
    
    for pkt in pcap:
        counts["total"] += 1
       
        packet = {}
        packet['ts'] = datetime.fromtimestamp(pkt.time).strftime('%Y-%m-%d %H:%M:%S')
        packet['id'] = counts["total"]
        
        if pkt.haslayer(IP):
            counts["ip"] += 1
            ip = pkt.getlayer(IP) 
            
            
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
        resultat[0]["trames"].append({ "id" : packet["id"],"IPSrc" : packet["src"][0], "IPDest" : packet["dst"][0] ,"PortSrc" : packet["src"][1], "PortDest" : packet["dst"][1] ,"Protocole" : packet["proto"]})

    #returnjson =  json.dumps(res, sort_keys=True)
    s = pcap.sessions()
    sessionId = 0
    for summary,data in s.iteritems():
        # summary est de la forme UDP 192.168.11.228:21893 > 208.67.222.222:53
        #TO DO Isoles le prot, les ip et ports dans le tableaux sessions
        #donnee=""
        #for pkt in data:
        #    if pkt.haslayer(IP):
        #         donnee += pkt.getlayer(IP).payload
        summ = summary.split(' ')
        if summ[0]=="UDP" or summ[0]=="TCP":
            src = summ[1].split(":")
            dest = summ[3].split(":")
            sessionId += 1
        else:
            src=None
            est=None
            
        if src != None:
            resultat[0]["sessions"].append({"id":sessionId,"IPSrc":src[0],"IPDest":dest[0],"PortSrc":src[1],"PortDest":dest[1],"Protocole":summ[0]})
        
    print "Done parsing, here are some statistics: "
    print "\t", counts
    
    return resultat