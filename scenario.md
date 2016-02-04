# Scenario d'utilisation du soft

Un attaquant dispose d'un fichier pcap créé à l'intérieur d'un réseau qu'il souhaite attaquer en boite noire. L'attaquant veut voir immédiatement les informations du pcap, et pouvoir lui même déduire des choses. L'identification d'un protocole non sécurisé est immédiate, mais voir que beaucoup de machines se connectent toute à une seule machine en DNS est très utile pour l'attaquant

- L'attaquant espère soutirer des informations sur le réseau :
- Les adresses IP identifiées
- les protocoles utilisés ( non chiffré, mal configurés? )
- Les nœuds importants et leur rôle (serveur DNS, DHCP, SMB, Mail, Kerberos...)
- Récupérer les données non chiffrées ayant transité

L'attaquant va repérer des choses intéressantes qui mérite plus d'informations. Il veut :

Filtrer les différentes visu par IP, Port, Protocole, Date, taille des paquets...
Obtenir d'autres visu moins générales : Zoom sur une IP / Plage d'IP

##Scénario

L'attaquant lance le serveur. Il upload son fichier pcap et attend le chargement des résultats.

La sidebar lui permet de voir tous les protocoles en jeux dans ce pcap :
- (LDAP,POP3,IMAP,SMTP,DNS,HTTP) sont intéressant,
- (LDAPS ,IMAPS,HTTPS ,KERBROS,ARP,ICMP,SMB) le sont moins.

La sidebar lui permet aussi de voir toutes les IP en jeux dans le pcap, et ainsi reperer des sous-réseau.

En filtrant sur les protocoles sont sécurisé, l'attaquant peut voir sur la vue en barre parallèle quelles machines sont non sécurisées. L'attaquant extrait alors les mots de passes et autres informations contenues dans les protocoles non sécurisés

L'attaquant observe ensuite la vue TreeMap. Il repère alors des IP ne dialoguant que dans un protocole : DHCP, DNS, SMB : cela lui permet d'identifier les serveur internes. En switchant de vue et en filtrant sur ces protocole l'hypothèse est validée.

Enfin, la vue géographique des IP permet d'identifier des sessions douteuses provenant de Russie. En filtrant sur ces IP, l'attaquant extrait le pcap correspondant uniquement à ces sessions. Celui lui permet d'étudier plus en profondeur (sur Wireshark) et d'observer des attaques menées depuis la russie


##L'interface d'acceuil


Plusieurs vues possibles 
Voir les nœuds les plus importants et deviner leur rôle: Un graphe TreeMap des IP en fonction de leur volume échangés et à l'intérieur leur protocoles utilisés
Avoir un apercu de la cartographie du réseau : Un graphe des liens entre IP avec des tailles de nœuds proportionnel au volume, et des couleurs de liens différents pour les protocoles, regroupant les IP locales d'un même sous réseau ensemble et les IP publique dans un sous-réseau

Une barre de menu comprenant les différents filtres disponibles
Un panel de contrôle sur la sélection : Si l'utilisateur clique sur un carré du TreeMap ou un lien du graphe, des informations sur l'hôte/la connexion apparaitront dans ce panel ainsi que des outils (télécharger le pcap de la connexion, les données transmises)
 
