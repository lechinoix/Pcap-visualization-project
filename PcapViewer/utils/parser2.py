from scapy.all import *
from datetime import datetime
import json
import sys
from models import Stat ,User, Packet, Session
from database import db_session,init_db
#from netaddr import IPNetwork, IPAddress

def hexdump(x):
    x = str(x)
    l = len(x)
    res = ""
    for i in range(l): 
        res += sane_color(x[i])
    return res

def initiate():
    init_db()
    # for el in Stat.query.all():
    #     db_session.delete(el)         


def get_protocol(pkt):
    protocol = "Autre"
    if pkt.haslayer(TCP):
        if pkt[TCP].dport == 7 or pkt[TCP].sport == 7:
            protocol = "ICMP"
        elif pkt[TCP].dport == 20 or pkt[TCP].sport == 20:
            protocol = "FTP"
        elif pkt[TCP].dport == 21 or pkt[TCP].sport == 21:
            protocol = "FTP"
        elif pkt[TCP].dport == 22 or pkt[TCP].sport == 22:
            protocol = "SSH"
        elif pkt[TCP].dport == 25 or pkt[TCP].sport == 25:
            protocol = "SMTP"
        elif pkt[TCP].dport == 80 or pkt[TCP].sport == 80:
            protocol = "HTTP"
        elif pkt[TCP].dport == 88 or pkt[TCP].sport == 88:
            protocol = "KERBEROS"
        elif pkt[TCP].dport == 110 or pkt[TCP].dport == 109 or pkt[TCP].sport == 110 or pkt[TCP].sport == 109:
            protocol = "POP3"
        elif pkt[TCP].dport == 115 or pkt[TCP].sport == 115:
            protocol = "SFTP"
        elif pkt[TCP].dport == 220 or pkt[TCP].dport == 143 or pkt[TCP].sport == 220 or pkt[TCP].sport == 143:
            protocol = "IMAP"
        elif pkt[TCP].dport == 389 or pkt[TCP].sport == 389:
            protocol = "LDAP"
        elif pkt[TCP].dport == 443 or pkt[TCP].sport == 443:
            protocol = "HTTPS"                
        elif pkt[TCP].dport == 445 or pkt[TCP].sport == 445:
            protocol = "SMB"
        elif pkt[TCP].dport == 636 or pkt[TCP].sport == 636:
            protocol = "LDAPS"
        elif pkt[TCP].dport == 993 or pkt[TCP].sport == 993:
            protocol = "IMAPS"
        elif pkt[TCP].dport == 995 or pkt[TCP].sport == 995:
            protocol = "POP3S"
    elif pkt.haslayer(UDP):
        if pkt[UDP].dport == 53 or pkt[UDP].sport == 53:
            protocol = "DNS"
    elif pkt.haslayer(ARP):
        protocol = "ARP"
    elif pkt.haslayer(ICMP):
        protocol = "ICMP"
    return protocol

def feed_stats(stat, packet):
    protocol = get_protocol(packet)
    stat["total"] +=1
    if stat.has_key(protocol):
        stat[protocol] +=1 
    else:
        stat[protocol] = 1  

#TO DO mettre a jour cette fonction
def feed_trames(pkt,session):

    timestamp = datetime.fromtimestamp(pkt.time).strftime('%Y-%m-%d %H:%M:%S')
    protocol = get_protocol(pkt)
    
    if pkt.haslayer(IP):
        ip = pkt.getlayer(IP) 
        hostSrc=ip.src
        hostDest=ip.src

        if ip.haslayer(TCP):
            tcp = ip.getlayer(TCP)
            portSrc = tcp.sport
            portDest = tcp.dport
            
        elif ip.haslayer(UDP):
            udp = ip.getlayer(UDP)
            portSrc = udp.sport
            portDest = udp.dport
            
        else:
            portSrc=None
            portDest=None
            
    elif pkt.haslayer(ARP):
        arp = pkt.getlayer(ARP)
        hostSrc = arp.psrc
        hostDest = arp.pdst  
        portSrc = None
        portDest = None

    if pkt.haslayer(Raw):
        data = {"data" :hexdump(pkt.getlayer(Raw))}
    else:
        data = {}
        
    P = Packet(hostSrc,hostDest,portSrc,portDest,protocol,data,timestamp,session)
    db_session.add(P)
    #database.insert_packet(packet)
    #res[0]["connexion"].append(packet)

#TO DO Probleme, la table Session a ete supprimee et je n'arrive pas a la remttre...
def extract_session(summary,data):
    
    s = summary.split(' ')
    # summary est de la forme UDP 192.168.11.228:21893 > 208.67.222.222:
    if s[0]=="TCP" or s[0]=="UDP":
        Src = s[1].split(":")
        Dst = s[3].split(":")
        hostSrc = Src[0]
        portSrc = Src[1]
        hostDest = Dst[0]
        portDest = Dst[1]
        protocol = s[0]
        if hostDest != "255.255.255.255":
            sess = Session(hostSrc,hostDest,portSrc,portDest,protocol) 
            db_session.add(sess) 
            for pkt in data:
                feed_trames(pkt,sess)

        #print "Session ajoutee"
         
        # for packet in data:
        #     nb += 1
        #     if packet.haslayer(Raw):
        #         payload += onlyascii(packet.getlayer(Raw).load) + "\n"
        # sess["Nombre"] = nb
        # sess["Payload"] = payload   

#Probleme : le volume est toujours egal a 64...
def feed_user(user,pkt,tid):

    if pkt.haslayer(IP):
        ip = pkt.getlayer(IP) 
        #if in_network(ip.src) or in_network(ip.src,"10.0.0.0/8") or in_network(ip.src,"172.16.0.0/12"):
        if True:
            protocol = get_protocol(ip)
            #print protocol
            if user.has_key(ip.src):
                user[ip.src]["Volume"]+=sys.getsizeof(ip)
                if user[ip.src]["Protocole"].has_key(protocol):
                    user[ip.src]["Protocole"][protocol]["Volumeout"]+=sys.getsizeof(ip)
                    user[ip.src]["Protocole"][protocol]["Nombreout"]+=1
                else:
                    #print "Ajout d'un nouveau protocol ("+protocol+") a "+ip.src
                    user[ip.src]["Protocole"][protocol]={
                        "Volumein": 0,
                        "Volumeout":sys.getsizeof(ip),
                        "Nombrein":0,
                        "Nombreout":1                      
                    }
            else:
                user[ip.src]={
                    "Volume": sys.getsizeof(ip),
                    "id":tid,
                    "Protocole":
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
                #print "Nouvel IP : "+ip.src
                tid +=1

        #elif in_network(ip.dst) or in_network(ip.dst,"10.0.0.0/8") or in_network(ip.dst,"172.16.0.0/12"):
            #protocol = get_protocol(ip)
            if user.has_key(ip.dst):
                user[ip.dst]["Volume"]+=sys.getsizeof(ip)
                if user[ip.dst]["Protocole"].has_key(protocol):
                    user[ip.dst]["Protocole"][protocol]["Volumein"]+=sys.getsizeof(ip)
                    user[ip.dst]["Protocole"][protocol]["Nombrein"]+=1
                else:
                    #print "Ajout d'un nouveau protocol ("+protocol+") a "+ip.dst
                    user[ip.dst]["Protocole"][protocol]={
                        "Volumein": sys.getsizeof(ip),
                        "Volumeout":0,
                        "Nombrein":1,
                        "Nombreout":0
                    }
            else:
                user[ip.dst]={
                    "Volume": sys.getsizeof(ip),
                    "id":tid,
                    "Protocole":
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
                #print "Nouvel IP : "+ip.dst
                tid +=1

    return tid 
            #print "Nouvel IP : "+ip.dst
    
def commit(user,stat):
    for el in user:
        U = User(el,user[el])
        db_session.add(U)
    print stat
    for el in stat:
        S = Stat(el,stat[el])
        db_session.add(S)

def parse(filename):
    """
    Parses pcap file and populate de PostgreSQL Database
    """
    try:
        initiate()
    except Exception as e:
        print e
    user={}
    stat={"total":0}
    #try:
    ttot = time.clock()
    pcap = rdpcap(filename)
    print "Temps de lecture du pcap : " + str(time.clock()-ttot)
    tid=0
    t0 = 0
    t1 =0
    t2= 0
    t3 = 0
    t4 = 0
    for pkt in pcap:
        t0 = time.clock()
        tid = feed_user(user,pkt,tid)
        t1 += time.clock() - t0
        t0 = time.clock()
        feed_stats(stat,pkt)
        t2 += time.clock()-t0

    t0 = time.clock()
    commit(user,stat)
    t4 += time.clock() - t0

    t0 = time.clock()
    s = pcap.sessions()
    for summary,data in s.iteritems():
        extract_session(summary,data)
    t3 += time.clock()-t0    

    print "Sessions & Packets generated in "+str(t3)+" seconds" 
    print "Treemap generated "+str(t1)+" seconds"
    #print json.dumps(user,indent=4)
    print "Stat generated "+str(t2)+" seconds"

    print "Done parsing"
# except Exception, e:
    #      return {"Error":e}
    #print "\n", web
    t0 = time.clock()
    db_session.commit()
    t4 += time.clock()-t0
    print "Commit took " + str(t4) + " seconds"
    return {}

#-----------------------------------UNUSED FUNCTION-----------------------------------------#

# def get_web(filename):
#     webpkts = []
#     result = ""
#     pcap = rdpcap(filename)
#     for packet in pcap:
#         if TCP in packet:
#             if packet.getlayer('TCP').dport == 80 or packet.getlayer('TCP').dport == 8080:
#                 webpkts.append(packet)
#     for packet in webpkts:
#         if packet.getlayer('TCP').flags == 24:
#             result = result + '''<div class="ui vertical segment"><p>'''
#             result = result + packet.getlayer('Raw').load.replace(' ','&nbsp;').replace('\n','<br/>')
#             result = result + '''</p></div>'''
#     if result == "":
#         result = '''<div class="ui vertical segment"><p>No WebView Packets!</p></div>'''
#     result = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\\x80-\\xff]').sub('', result)
#     return result

# def get_mail(filename):
#     mailpkts = []
#     result = "<p>"
#     pcap = rdpcap(filename)
#     for packet in pcap:
#         if TCP in packet:
#             if packet.getlayer('TCP').dport == 110 or packet.getlayer('TCP').sport == 110 or packet.getlayer('TCP').dport == 143 or packet.getlayer('TCP').sport == 143 :
#                 mailpkts.append(packet)
#     for packet in mailpkts:
#         if packet.getlayer('TCP').flags == 24:
#             result = result + packet.getlayer('Raw').load.replace(' ','&nbsp;').replace('\n','<br/>')
#     if result == "<p>":
#         result = result + "No Mail Packets!"
#     result = result + "</p>"
#     result = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\\x80-\\xff]').sub('', result)
#     return result

# def in_network(ip,network = "192.168.0.0/16"):

#     if IPAddress(ip) in IPNetwork(network):
#         return True
#     else:
#         return False