#!/bin/sh
rsync -avz -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/romsGP/ /Volumes/MTLION/data/romsGP/
