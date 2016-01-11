# Partitionnement du projet :

## Partie Analyse et réduction de la trace :

Traitement avec scapy, interfaçage avec Ettercap.

### Travail à fournir :

- Créer une API Python d'Ettercap
- Disséquer la trace réseau en un objet mieux manipulable (JSON ?)
- Réduction de la taille de la trace

### Outils :

- Wireshark
- Ettercap
- Scapy

## Partie IHM et visualisation :

Utilisation de ces données pour réaliser une IHM et un visualisation interactive

### Travail à fournir :

- Faire un design plus poussé de l'application
- Prendre en main D3.js
- Réaliser l'IHM

### Outils :

- Gimp
- D3.js
- Symfony 2

## Réflexion à fournir :

- Comment réduire la trace ?
- Que veut-on visualiser ?

### Eléments de réponse :

On compte réduire la trace en la réorganisant sous forme de sessions et en rendant possible une exploration de la trace en largeur et en profondeur.

Solutions de visu : visu en réseau de communication avec filtres associés (timeline, protocole, host address), possibilité de zoom in sur une partie intéressante ou un participant et de faire tourner des analyses sur une portion de la capture.
