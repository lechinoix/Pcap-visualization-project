# Pcap-visualization-project


This tool is a web based pcap visualisation tool, using a **Flask** server to parse a pcap with **scapy** and store it in a postgresql database and a web-browser interface to display datas with **D3.js**.

Use this tool if you want to figure out how the network looks like, the protocol used during the capture, identify the main actors of the network such as servers, and see unsecured exchanged data.

It will be possible to target a part of a pcap thanks to filters (on hosts, services, time...), and then processing analysis on reconstructed pcap.


## Getting started

### Installation

Clone project from https://github.com/lechinoix/Pcap-visualization-project.git

You need to have python 2.7 or later and to download Flask (http://flask.pocoo.org/docs/0.10/installation/)

Then you need to set up the database.

First, check that you installed postgresql.

```
$ which psql
/usr/bin/psql
```

Then create a new user and a database.

```
$ sudo -u postgres createuser -Pd username
Enter password for new role: 
Enter it again:
$ createdb -U username --locale=en_US.utf-8 -E utf-8 -O username PcapViewer -T template0
```

Install psycopg2, Flask-Alchemy, Flask-SocketIO and Eventlet :

```
$ sudo apt-get install python-psycopg2
$ pip install Flask-SQLAlchemy
$ pip install flask-socketio
$ pip install eventlet
```

Go to PcapVierwer/config/default.py and change the database URI :

```
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/PcapViewer'
```

Then, initialize the database with :

```
$ cd path/to/PcapViewer
$ python
>>> from database import init_db
>>> init_db()
```

Ready to go !

To start the application run :

```
$ python /path/to/PcapViewer/app.py 
```

Then, you can access it from a browser such as Chrome or Firefox at http://localhost:5000/

### Start a new visualisation

Go to the Pcap Files menu, then click on add new pcap. Choose your pcap file and upload it. Wait for the file to be processed and then select it in the Pcap list.

### How can you use the tool ?

After starting the application, open your browser and load the following URL : 

```
http://localhost:5000/
```

You can easily upload your pcap file, its size must be under 50Mo though. On the sidebar you can visualize the different IP identified and the protocols used. There are two visualisation mode : Treemap & Parallel

Start looking at the parallel view. Each line represents a session established during the capture. You can easily see the source and destination IP and port, as well as the procotol. It is possible to switch axes by clicking and dragging on it. This view helps you to identify servers (DNS, Kerberos, SMB, mail..) and most important IP address. You can easily filter protocols or IP to clearify the view. You can easily filter an address range by selecting it directly on the axe with your mouse. Filtering on unsecured protocol helps you finding which IP aren't configured correctly.

Then start looking at the treemap visu. This gives you a good idea about what the network looks like globally and find the most importants networks in the network in terms of volume exchanged or number of packets exchanged. You can remove uninteresting nodes by filtering the hosts on the left panel.

Under the views, you can see packet detail and the data exchanged for each filtered session. For unsecured protocols, the data of each packet of the session has been aggregated, as a "Follow TCP Stream" command would do in Wireshark.

Look more closely at those, with the network visualization of its communications with other hosts. This view could be a tree with the node on top and then ramifications with the communications by protocol to different users. Big users could be written bigger.

There will be an analysis button at the bottom of this bar to run analysis on the current selection.

Unsecure protocols will be highlighted by default, and it will be possible to follow TCP stream on chosen clear sessions to see if he can get informations. This feature will be displayed on a right bar or under the graph, we'll see.

### How data will be processed ?

Each packet will be scanned and we will extract information from it. A postgresql database will be created on these infos. The structure is detailed in (schema.json)[schema.json]

We think about processing data in background while displaying the current content of the database. We will need to launch another thread to process the data in background, or to regularly call an update function in AJAX to refresh the content. We don't know yet if it can be done on the Flask test server or if we will have to had a new techno above it.


## The tools we used :

### Python tools

**Flask :** A micro web-framework python based that offers minimal services like templating and routing.

**Scapy :** A python library to manipulate packets and pcap files.

### Web tools

**D3.js :** A data visualisation library which permits svg creation along a provided data.

**Bootstrap :** Web framework to ensure scalability of the application and precreated useful components.

<br><hr><br>

#### Some interesting docs about wireshark visu projects :

*A whitepaper about packet analysis :* [Practical Packet Analysis] (http://repository.root-me.org/R%C3%A9seau/EN%20-%20Practical%20packet%20analysis%20-%20Wireshark.pdf)

*A wireshark plugin coded during a google summer code :* [Wireviz](https://www.wireshark.org/lists/wireshark-dev/201107/msg00218.html)

*All wireshark plugins developped during this GSoC :* [GSoC wireshark projects](https://www.honeynet.org/node/716)

*Some guy asking why we are so late in our project :* [Where is the visu ?](https://ask.wireshark.org/questions/9884/data-visualization-options-in-wireshark)


