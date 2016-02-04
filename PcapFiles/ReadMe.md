### Our Pcap database

Pcaps for testing. Progressive size of company network dumps. 

- Extracted from : ftp://ftp.bro-ids.org/enterprise-traces/hdr-traces05/
- Original format : .dump.anon
- Desired format : .pcap
- Converted with wireshark command line tool text2pcap : text2pcap -d inputFile.dump.anon outputFile.pcap

## Problem :

The format is not the good one :

Current format :

3030 3030 3030 20d4 c320 b2a1 0200 0400
0000 0000 0000 0000 ffff 0000 0100 0000
01ca 6141 2714 0000 3600 0000 ea05 0000
28cc 34c9 cc20 8020 2098 3b20 b9ec 0800
4500 05dc b653 4000 fc06 6a33 83f3 e3c1
8003 70dc 0801 058c e30f 2e2b d5c4 9294
5010 60f4 6976 0000 01ca 6141 b263 0000

Wanted format :

000000 d4 c3 b2 a1 02 00 04 00 00 00 00 00 00 00 00 00
000016 ff ff 00 00 01 00 00 00 01 ca 61 41 27 14 00 00
000032 36 00 00 00 ea 05 00 00 28 cc 34 c9 cc 20 80 0b
000048 98 3b b9 ec 08 00 45 00 05 dc b6 53 40 00 fc 06
000064 6a 33 83 f3 e3 c1 80 03 70 dc 08 01 05 8c e3 0f
000080 2e 2b d5 c4 92 94 50 10 60 f4 69 76 00 00 01 ca
000096 61 41 b2 63 00 00 36 00 00 00 3c 00 00 00 b8 d6

We use a small python script to convert it (format.py)

Command : python format.py input.dump.anon | text2pcap -o hex - output.pcap

It works for very small files butt not on large ones.
