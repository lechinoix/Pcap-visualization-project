# Pcap-visualization-project


Web based pcap visualisation tool, using a **Flask** server to parse a pcap with **scapy** and store it in a postgresql database and a web-browser interface to display datas with **D3.js**.

It will be possible to target a part of a pcap thanks to filters (on hosts, services, time...), and then processing analysis on reconstructed pcap with classic pentest tools like **Ettercap** or **ChaosReader**.


## Getting started

### Installation

Clone project from https://github.com/lechinoix/Pcap-visualization-project.git

You need to have python 2.7 or later and to download Flask (http://flask.pocoo.org/docs/0.10/installation/)

Then run :

```python /path/to/PcapViewer/app.py ```

Then, you can access the app from a browser such as Chrome or Firefox at http://localhost:5000/

### Start a new visualisation

Go to the Pcap Files menu, then click on add new pcap. Choose your pcap file and upload it. Wait for the file to be processed and then select it in the Pcap list.

### How can you use the tool ?

Start looking at the treemap visu, and find the most importants nodes in the network. You can remove uninteresting nodes by clicking on a close button of their square. 

Look more closely at those, with the network visualization of its communications with other hosts. This view could be a tree with the node on top and then ramifications with the communications by protocol to different users. Big users could be written bigger.

This could also be seen on the parallel view that gives and idea about what the network looks like globally. You could reload the tool with only certain users, and only certain services, or remove one of those in the sidebar.

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

### Pentest tools

**Chaos reader :** Usefull to reconstruct files or images. 

**Ettercap :** Can process a pcap to catch passwords, detect OS and other passive analysis. Offers an API that we need to interface with our python program.

<br><hr><br>

#### Some interesting docs about wireshark visu projects :

*A wireshark plugin coded during a google summer code :* [Wireviz](https://www.wireshark.org/lists/wireshark-dev/201107/msg00218.html)

*All wireshark plugins developped during this GSoC :* [GSoC wireshark projects](https://www.honeynet.org/node/716)

*Some guy asking why we are so late in our project :* [Where is the visu ?](https://ask.wireshark.org/questions/9884/data-visualization-options-in-wireshark)

*Read me for wireshark plugin :* [Plugin Wireshark](https://code.wireshark.org/review/gitweb?p=wireshark.git;a=blob_plain;f=doc/README.plugins)

