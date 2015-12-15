# Pcap-visualization-project

A pcap visualization tool for pentesters, discovering configuration faults, usefull information and other incredible stuff

## Point sur la situation :

### Chaos reader :


- Ce qu'il y a de visuel dans des pcap : tout ce qui est images, on peut en faire la reconstruction
- Les pages web, c'est pareil on peut les reconstruire

### Wireshark :


- Meilleur interfaçage pour une vue pentesters des trames plutôt que la vue "liste" de wireshark
- Problème : ne doit pas réduire les possibilités par rapport à wireshark, si il faut reforger le pcap chaque fois que l'on veut faire une opération dessus (filtrage, follow stream...) l'outil est inutile
- Il faut quand même pouvoir appliquer des filtres et suivre des flux, ou sinon modifier l'interface de wireshark directement pour profiter des outils qu'il offre sans en perdre les fonctionnalités

### Ettercap :


- Propose des outils orientés pentest actif (rejeu, mitm...) et passif (détection d'OS, récupération de mdp...)
- Offre une API de plugin


### Bilan :

- Les fonctions de filtrage et de follow tcp stream sont pas trop compliquées à refaire, on peut donc essayer de faire une interface graphique d'ettercap ou d'un outil de pentest qui permette de mieux visualiser le trafic en l'interfaçant directement avec des outils de pentest.
- Il faudrait faire en sorte d'être à peu près sûr de ne pas offrir un service qui soit trop pauvre en fonctionnalités et qui donc serait inutile, ou de trouver une fonctionalité particulière qui fasse en sorte que l'outil soit intéressant en soi.
- Tant qu'on a pas d'idée géniale sur quelque chose à mettre en valeur via une visualisation, on peut rester sur l'idée de l'interfaçage graphique de la trame réseau avec des outils de pentest

<br><hr><br>

###### Some interesting docs about wireshark visu projects :
*A wireshark plugin coded during a google summer code :* [Wireviz](https://www.wireshark.org/lists/wireshark-dev/201107/msg00218.html)
*All wireshark plugins developped during this GSoC :* [GSoC wireshark projects](https://www.honeynet.org/node/716)
*Some guy asking why we are so late in our project :* [Where is the visu ?](https://ask.wireshark.org/questions/9884/data-visualization-options-in-wireshark)
*Read me for wireshark plugin :* [Plugin Wireshark](https://code.wireshark.org/review/gitweb?p=wireshark.git;a=blob_plain;f=doc/README.plugins)

 
