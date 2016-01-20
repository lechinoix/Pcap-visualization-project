#! /usr/bin/python
# -*- coding:utf-8 -*-

import sys
with open(sys.argv[1]) as f:
    count = 0
    for line in f:
        if line == '\n': pass
        else:
            string = [i[:2] for i in line.split()]
            for i in range(len(string)):
                string.insert(i*2+1, line.split()[i][2:])
            print "%06d" % count + " " + ' '.join(string)
            count += len(string) 
