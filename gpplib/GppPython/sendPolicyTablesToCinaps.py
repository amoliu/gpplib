#!/usr/bin/env python

from os import system

rsyncCmd = 'rsync -avz PolicyTable*.shelve -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/PolicyTables/'
print rsyncCmd
system( rsyncCmd )
