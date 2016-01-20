from scapy.all import *
from datetime import datetime
import json

def onlyascii (text):
    #if ord(char) < 48 or ord(char) > 127 : return '.'
    #else: return char
     return ''.join([i if ord(i) < 128 else '. ' for i in text])

def get_statistics(filename):
    tcp = 0
    udp = 0
    arp = 0
    icmp = 0
    other = 0
    pcapstat = {'tcp':0,'udp':0,'arp':0,'icmp':0,'other':0,'total':0}
    pcap = rdpcap(filename)
    for packet in pcap:
        if TCP in packet:
            tcp = tcp + 1
        elif UDP in packet:
            udp = udp + 1
        elif ARP in packet:
            arp = arp + 1
        elif ICMP in packet:
            icmp = icmp + 1
        else:
            other = other + 1
    pcapstat['tcp'] = str(tcp)
    pcapstat['udp'] = str(udp)
    pcapstat['arp'] = str(arp)
    pcapstat['icmp'] = str(icmp)
    pcapstat['other'] = str(icmp)
    pcapstat['total'] = str(tcp + udp + arp + icmp + other)
    return pcapstat    

def get_web(filename):
    webpkts = []
    result = ""
    pcap = rdpcap(filename)
    for packet in pcap:
        if TCP in packet:
            if packet.getlayer('TCP').dport == 80 or packet.getlayer('TCP').dport == 8080:
                webpkts.append(packet)
    for packet in webpkts:
        if packet.getlayer('TCP').flags == 24:
            result = result + '''<div class="ui vertical segment"><p>'''
            result = result + packet.getlayer('Raw').load.replace(' ','&nbsp;').replace('\n','<br/>')
            result = result + '''</p></div>'''
    if result == "":
        result = '''<div class="ui vertical segment"><p>No WebView Packets!</p></div>'''
    result = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\\x80-\\xff]').sub('', result)
    return result

def get_mail(filename):
    mailpkts = []
    result = "<p>"
    pcap = rdpcap(filename)
    for packet in pcap:
        if TCP in packet:
            if packet.getlayer('TCP').dport == 110 or packet.getlayer('TCP').sport == 110 or packet.getlayer('TCP').dport == 143 or packet.getlayer('TCP').sport == 143 :
                mailpkts.append(packet)
    for packet in mailpkts:
        if packet.getlayer('TCP').flags == 24:
            result = result + packet.getlayer('Raw').load.replace(' ','&nbsp;').replace('\n','<br/>')
    if result == "<p>":
        result = result + "No Mail Packets!"
    result = result + "</p>"
    result = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\\x80-\\xff]').sub('', result)
    return result

def parse(filename):
    """
    Parses pcap file into JSON files
    """
    pcap = rdpcap(filename)
    resultat={"trames":[],"sessions":[]}
    stats = get_statistics(filename)
    #web = get_web(filename)
    #mail = get_mail(filename)
    
    for pkt in pcap:
        #stats["total"] += 1
       
        packet = {}
        packet['ts'] = datetime.fromtimestamp(pkt.time).strftime('%Y-%m-%d %H:%M:%S')
        packet['id'] = stats["total"]
        
        if pkt.haslayer(IP):
            #stats["ip"] += 1
            ip = pkt.getlayer(IP) 
            
            
            if ip.haslayer(TCP):
                #stats["tcp"] += 1
                tcp = ip.getlayer(TCP)
                packet["proto"] = "tcp"
                packet["src"] = ( ip.src, tcp.sport )
                packet["dst"] = ( ip.dst, tcp.dport )
                
            elif ip.haslayer(UDP):
                #stats["udp"] += 1
                udp = ip.getlayer(UDP)
                packet["proto"] = "udp"
                packet["src"] = ( ip.src, udp.sport )
                packet["dst"] = ( ip.dst, udp.dport )
                
            elif ip.haslayer(ICMP):
                #stats["icmp"] += 1
                icmp = ip.getlayer(ICMP)
                packet["proto"] = "icmp"
                packet["src"] = ( ip.src, None )
                packet["dst"] = ( ip.dst, None )
                
            else:
                #pkt.show()
                continue
                
        elif pkt.haslayer(ARP):
            #stats["arp"] += 1 
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
        resultat["trames"].append(
                            { 
                            "id" : packet["id"],
                            "IPSrc" : packet["src"][0], 
                            "IPDest" : packet["dst"][0] ,
                            "PortSrc" : packet["src"][1], 
                            "PortDest" : packet["dst"][1] ,
                            "Protocole" : packet["proto"]
                            })

    #returnjson =  json.dumps(res, sort_keys=True)
    s = pcap.sessions()
    sessionId = 0
    for summary,data in s.iteritems():
        # summary est de la forme UDP 192.168.11.228:21893 > 208.67.222.222:53

        # donnee=""
        # for pkt in data:
        #     if pkt.haslayer(IP):
        #         ip = pkt.getlayer(IP) 
        #         if  ip.haslayer(TCP):
        #             print "yes"
        #             print pkt[TCP].payload
        #             # add it to the other string
        #              #donnee += filter(onlyascii, pkt[TCP].payload[:1])
        #             donnee += bytes
        #         elif ip.haslayer(UDP):
        #             #donnee += filter(onlyascii, pkt[UDP].payload[:1])
        #             print None
        # print donnee
        
        summ = summary.split(' ')
        if summ[0]=="UDP" or summ[0]=="TCP":
            src = summ[1].split(":")
            dest = summ[3].split(":")
            sessionId += 1
        else:
            src=None
            est=None
            
        if src != None:
            resultat["sessions"].append(
                                {
                                "id":sessionId,
                                "IPSrc":src[0],
                                "IPDest":dest[0],
                                "PortSrc":src[1],
                                "PortDest":dest[1],
                                "Protocole":summ[0],
                                #"Donnee":donnee
                                })
        
    print "Done parsing, here are some statistics: "
    print "\t", stats
    #print "\n", web
    
    return resultat
    
