from scapy.all import *
from datetime import datetime
import json
import sys
from models import Stat ,User, Packet, Session
from database import db_session
#from netaddr import IPNetwork, IPAddress

def hexdump(x):
    x = str(x)
    l = len(x)
    res = ""
    for i in range(l): 
        res += sane_color(x[i])
    return res

def initiate():
    for el in Stat.query.all():
        db_session.delete(el)
    liste = ["TOTAL","Autre","HTTP","HTTPS","LDAP","LDAPS","SMB","FTP","SSH","SMTP","POP3","IMAP","KERBEROS","DNS","ARP","ICMP"]
    for el in liste:
        S = Stat(el,0)
        db_session.add(S)

    for el in User.query.all():
        db_session.delete(el) 
    for el in Session.query.all():
        db_session.delete(el)   
    db_session.commit()

def get_protocol(pkt):
    protocol = "Autre"
    if pkt.haslayer(TCP):
        if pkt[TCP].dport == 7 or pkt[TCP].sport == 7:
            protocol = "ICMP"
        elif pkt[TCP].dport == 80 or pkt[TCP].sport == 80:
            protocol = "HTTP"
        elif pkt[TCP].dport == 443 or pkt[TCP].sport == 443:
            protocol = "HTTPS"                
        elif pkt[TCP].dport == 445 or pkt[TCP].sport == 445:
            protocol = "SMB"
        elif pkt[TCP].dport == 21 or pkt[TCP].sport == 21:
            protocol = "FTP"
        elif pkt[TCP].dport == 22 or pkt[TCP].sport == 22:
            protocol = "SSH"
        elif pkt[TCP].dport == 25 or pkt[TCP].sport == 25:
            protocol = "SMTP"
        elif pkt[TCP].dport == 88 or pkt[TCP].sport == 88:
            protocol = "KERBEROS"
        elif pkt[TCP].dport == 110 or pkt[TCP].sport == 110:
            protocol = "POP3"
        elif pkt[TCP].dport == 110 or pkt[TCP].sport == 110:
            protocol = "IMAP"
        elif pkt[TCP].dport == 389 or pkt[TCP].sport == 110:
            protocol = "LDAP"
        elif pkt[TCP].dport == 636 or pkt[TCP].sport == 110:
            protocol = "LDAPS"
    elif pkt.haslayer(UDP):
        if pkt[UDP].dport == 53 or pkt[UDP].sport == 53:
            protocol = "DNS"
    elif pkt.haslayer(ARP):
        protocol = "ARP"
    elif pkt.haslayer(ICMP):
        protocol = "ICMP"
    return protocol

def feed_stats(packet):
    protocol = get_protocol(packet)
    S = Stat.query.filter(Stat.name==protocol).first()
    if S != None :
        S.value +=1
    T = Stat.query.filter(Stat.name=="TOTAL").first()
    if T != None :
        T.value +=1
    # stats["total"] +=1
    # if stats.has_key(protocol):
    #     stats[protocol] +=1 
    # else:
    #     stats[protocol] = 1  

def feed_trames(trames,data,sessionId):

    try:
        id = trames[-1]["id"]
    except:
        id = 0
    
    for pkt in data:
        id += 1
        packet={}
        packet['timestamp'] = datetime.fromtimestamp(pkt.time).strftime('%Y-%m-%d %H:%M:%S')
        packet['id'] = id
        packet['sessionId'] = sessionId
        protocol = get_protocol(pkt)

        if pkt.haslayer(IP):
            #stats["ip"] += 1
            ip = pkt.getlayer(IP) 

            packet["proto"]=protocol
            packet["IpSrc"]=ip.src
            packet["IpDest"]=ip.dst

            if ip.haslayer(TCP):
                tcp = ip.getlayer(TCP)
                packet["PortSrc"] = tcp.sport
                packet["PortDst"] = tcp.dport
                
            elif ip.haslayer(UDP):
                udp = ip.getlayer(UDP)
                packet["PortSrc"] = udp.sport
                packet["PortDst"] = udp.dport
                
            else:
                packet["PortSrc"]=None
                packet["PortDest"]=None
                
        elif pkt.haslayer(ARP):
            arp = pkt.getlayer(ARP)
            packet["proto"] = "ARP"
            packet["src"] = ( arp.psrc , None )
            packet["dst"] = ( arp.pdst, None )

        if pkt.haslayer(Raw):
            packet["payload"] = hexdump(pkt.getlayer(Raw))
        
        trames.append(packet)

def extract_session(summary,sessionId):
    
    summ = summary.split(' ')
    # summary est de la forme UDP 192.168.11.228:21893 > 208.67.222.222:
    if summ[0]=="TCP" or summ[0]=="UDP":
        #sess = Session(summ[1].split(":")[0], summ[3].split(":")[0], summ[1].split(":")[1], summ[3].split(":")[1],summ[0]) 
        #db_session.add(sess)     

#Probleme : le volume est toujours egal a 64...
def feed_user(pkt):

    if pkt.haslayer(IP):
        ip = pkt.getlayer(IP) 
        #if in_network(ip.src) or in_network(ip.src,"10.0.0.0/8") or in_network(ip.src,"172.16.0.0/12"):
        protocol = get_protocol(ip)
        #print protocol
        U = User.query.filter(User.address==ip.src).first()
        
        if U != None:
            U.exchanged["Volume"]+=sys.getsizeof(ip)
            
            if U.exchanged["Protocoles"].has_key(protocol):
                U.exchanged["Protocoles"][protocol]["Volumeout"]+=sys.getsizeof(ip)
                U.exchanged["Protocoles"][protocol]["Nombreout"]+=1
                # print "Mise a jour :",
                # print res,
                # print " (" + protocol + ")"
                res = U
                db_session.delete(U)
                U=User(res.address,res.exchanged)
                db_session.add(U)
                db_session.commit()
            else:
                print "Ajout d'un nouveau protocol ("+protocol+") a "+ip.src
                U.exchanged["Protocoles"][protocol]={
                    "Volumein": 0,
                    "Volumeout":sys.getsizeof(ip),
                    "Nombrein":0,
                    "Nombreout":1                      
                }
                res = U
                db_session.delete(U)
                U = User(res.address,res.exchanged)
                db_session.add(U)
        else:
            U = User(ip.src,{})
            U.exchanged={
                "Volume": sys.getsizeof(ip),
                "Protocoles":
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
            db_session.add(U)
        db_session.commit()
            #print "Nouvel IP : "+ip.src
        
        U = User.query.filter(User.address==ip.dst).first()
        #protocol = get_protocol(ip)
        if U != None:
            U.exchanged["Volume"]+=sys.getsizeof(ip)
            if U.exchanged["Protocoles"].has_key(protocol):
                U.exchanged["Protocoles"][protocol]["Volumein"]+=sys.getsizeof(ip)
                U.exchanged["Protocoles"][protocol]["Nombrein"]+=1
                res = U
                db_session.delete(U)
                U = User(res.address,res.exchanged)
                db_session.add(U)
            else:
                print "Ajout d'un nouveau protocol ("+protocol+") a "+ip.dst
                U.exchanged["Protocoles"][protocol]={
                    "Volumein": sys.getsizeof(ip),
                    "Volumeout":0,
                    "Nombrein":1,
                    "Nombreout":0
                }
                res = U
                db_session.delete(U)
                U = User(res.address,res.exchanged)
                db_session.add(U)
        else:
            U = User(ip.dst,{})
            U.exchanged={
                "Volume": sys.getsizeof(ip),
                "Protocoles":
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
            db_session.add(U)
        db_session.commit()
            #print "Nouvel IP : "+ip.dst
    

def parse(filename):
    """
    Parses pcap file and populate de PostgreSQL Database
    """
    try:
        # Stat.query.execute.drop_all()
        # Stat.query.execute.create_all()
        initiate()
        #print dir(db_session.class.query)
        #db_session.Stat.class.all
    except Exception as e:
        print e
    #try:
    ttot = time.clock()
    pcap = rdpcap(filename)
    print "Temps de lecture du pcap : " + str(time.clock()-ttot)

    resultat={"trames":[]}
    t0 = 0
    t1 =0
    t2= 0
    t3 = 0
    for pkt in pcap:
        t0 = time.clock()
        feed_user(pkt)
        t2 += time.clock() - t0
        feed_stats(pkt)
    #returnjson =  json.dumps(res, sort_keys=True)
    s = pcap.sessions()
    sessionId = 0
    for summary,data in s.iteritems():
        sessionId+=1
        t0 = time.clock()
        extract_session(summary,sessionId)
        t3 += time.clock()-t0
        t0 = time.clock()
        feed_trames(resultat["trames"],data,sessionId)
        t1 += time.clock() - t0

    print "Trames generated in "+str(t1)+" seconds"
    #print json.dumps(resultat["sessions"],indent=4) 
    print "Sessions generated in "+str(t3)+" seconds"
    #print json.dumps(resultat["sessions"],indent=4)    
    print "Treemap generated "+str(t2)+" seconds"
    #print json.dumps(resultat["user"],indent=4)

    print "Done parsing"
# except Exception, e:
    #      return {"Error":e}
    #print "\n", web
    db_session.commit()
    return resultat

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