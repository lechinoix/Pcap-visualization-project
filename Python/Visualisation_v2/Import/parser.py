from scapy.all import *
from datetime import datetime
import json
import sys

def onlyascii (text):
    #if ord(char) < 48 or ord(char) > 127 : return '.'
    #else: return char
     return ''.join([i if ord(i) < 128 else '. ' for i in text])


def get_protocol(ip):

    protocol = "Autre"
    if ip.haslayer(TCP):
        if ip[TCP].dport == 80 or ip[TCP].sport == 80:
            protocol = "HTTP"
        elif ip[TCP].dport == 443 or ip[TCP].sport == 443:
            protocol = "HTTPS"                
        elif ip[TCP].dport == 445 or ip[TCP].sport == 445:
            protocol = "SMB"
        elif ip[TCP].dport == 21 or ip[TCP].sport == 21:
            protocol = "FTP"
        elif ip[TCP].dport == 22 or ip[TCP].sport == 22:
            protocol = "SSH"
        elif ip[TCP].dport == 25 or ip[TCP].sport == 25:
            protocol = "SMTP"
        elif ip[TCP].dport == 88 or ip[TCP].sport == 88:
            protocol = "KERBEROS"
        elif ip[TCP].dport == 110 or ip[TCP].sport == 110:
            protocol = "POP3"
    if ip.haslayer(UDP):
        if ip[UDP].dport == 53 or ip[UDP].sport == 53:
            protocol = "DNS"
    return protocol

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

def extract_trame(pkt,id):

        packet = {}
        packet['ts'] = datetime.fromtimestamp(pkt.time).strftime('%Y-%m-%d %H:%M:%S')
        packet['id'] = id
        
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
                
        elif pkt.haslayer(ARP):
            #stats["arp"] += 1 
            arp = pkt.getlayer(ARP)
            
            packet["proto"] = "arp"
            packet["src"] = ( arp.psrc , None )
            packet["dst"] = ( arp.pdst, None )  
            
        #print "\tprocessing pkt w/ timestamp %s, %s -> %s..." % ( packet["ts"], packet["src"][0], packet["dst"][0] )
        #database.insert_packet(packet)
        #res[0]["connexion"].append(packet)
        return packet

def extract_session(summary,data,sessionId):
    sess = {}
    summ = summary.split(' ')
    payload=""
    # summary est de la forme UDP 192.168.11.228:21893 > 208.67.222.222:53
    if summ[0]=="TCP":
        sess["Id"] = sessionId + 1
        sess["IpSrc"]= summ[1].split(":")[0]
        sess["PortSrc"]= summ[1].split(":")[1]    
        sess["IpDest"]= summ[3].split(":")[0]
        sess["PortDest"]= summ[3].split(":")[1]      
        sess["Protocole"] = summ[0]
        # print "----------------------------------------------------"
        # print data
        # print "----------------------------------------------------"
        #sess["Payload"] = str(data[0].getlayer(Raw).load)
        #if data[0].haslayer(Raw): print data[0].getlayer(Raw).load
        return sess        
    else:
        return None
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
    
#Probleme : le volume est toujours egal a 64...
def feed_treemap(treemap,pkt,tid):

    if pkt.haslayer(IP):
        ip = pkt.getlayer(IP) 
        protocol = get_protocol(ip)

        if treemap.has_key(ip.src):
            treemap[ip.src]["Volume"]+=sys.getsizeof(ip)
            if treemap[ip.src]["Protocol"].has_key(protocol):
                treemap[ip.src]["Protocol"][protocol]["Volumeout"]+=sys.getsizeof(ip)
                treemap[ip.src]["Protocol"][protocol]["Nombreout"]+=1
            else:
                print "Ajout d'un nouveau protocol ("+protocol+") a "+ip.src
                treemap[ip.src]["Protocol"][protocol]={
                    "Volumein": 0,
                    "Volumeout":sys.getsizeof(ip),
                    "Nombrein":0,
                    "Nombreout":1                      
                }
        else:
            treemap[ip.src]={
                "Volume": sys.getsizeof(ip),
                "id":tid,
                "Protocol":
                  {
                      protocol:
                      {
                        "Volumein":0,
                        "Volumeout":sys.getsizeof(ip),
                        "Nombrein":0,
                        "Nombreout":1
                      }
                  }
            }
            print "Nouvel IP : "+ip.src
            tid +=1

        if treemap.has_key(ip.dst):
            treemap[ip.dst]["Volume"]+=sys.getsizeof(ip)
            if treemap[ip.dst]["Protocol"].has_key(protocol):
                treemap[ip.dst]["Protocol"][protocol]["Volumein"]+=sys.getsizeof(ip)
                treemap[ip.dst]["Protocol"][protocol]["Nombrein"]+=1
            else:
                print "Ajout d'un nouveau protocol ("+protocol+") a "+ip.dst
                treemap[ip.dst]["Protocol"][protocol]={
                    "Volumein": sys.getsizeof(ip),
                    "Volumeout":0,
                    "Nombrein":1,
                    "Nombreout":0
                }
        else:
            treemap[ip.dst]={
                "Volume": sys.getsizeof(ip),
                "id":tid,
                "Protocol":
                  {
                      protocol:
                      {
                        "Volumein": sys.getsizeof(ip),
                        "Volumeout":0,
                        "Nombrein":1,
                        "Nombreout":0
                      }
                  }
            }
            print "Nouvel IP : "+ip.dst+", prot :"+protocol
            tid +=1

    return tid 

def parse(filename):
    """
    Parses pcap file into JSON files
    """
    pcap = rdpcap(filename)
    resultat={"trames":[],"sessions":[],"treemap":{}}
    stats = get_statistics(filename)
        
    #web = get_web(filename)
    #mail = get_mail(filename)
    id=0
    tid=0
    for pkt in pcap:
        id += 1
        packet = extract_trame(pkt,id)
        resultat["trames"].append(packet)
        tid = feed_treemap(resultat["treemap"],pkt,tid)
    #returnjson =  json.dumps(res, sort_keys=True)
    
    s = pcap.sessions()
    sessionId = 0
    for summary,data in s.iteritems():
        sess = extract_session(summary,data,sessionId)
        if sess != None:
            sessionId = sess["Id"]
            resultat["sessions"].append(sess)
        
    print "Treemap generated :"
    print json.dumps(resultat["treemap"],indent=4)
    # for x in resultat["treemap"]:
       #  print (x)
       #  for y in resultat["treemap"][x]:
       #      print (y,':',resultat["treemap"][x][y])

    print "Done parsing, here are some statistics: "
    print "\t", stats
    #print "\n", web
    
    return resultat