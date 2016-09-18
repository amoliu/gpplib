#!/bin/sh
#
# Sync data with the datasets directory on cinaps.usc.edu
# Place this in the myDataDir+'gliderModelNS' directory.
# Sync will automatically create the gliderModel3 and gliderModelGP2 directories.

#rsync -avz -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/gliderModelNS/ ./ 
rsync -avz -e "ssh -l ampereir" ampereir@asimov.usc.edu:~/data/gliderModelNS/ ./

#rsync -avz -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/NoisyGliderModels/gliderModel3_201308*.shelf ../gliderModel3/
rsync -avz -e "ssh -l ampereir" ampereir@asimov.usc.edu:~/data/gliderModel3/gliderModel3_201308*.shelf ../gliderModel3/

rsync -avz -e "ssh -l ampereir" ampereir@asimov.usc.edu:~/data/gliderModelGP2/gliderModelGP2_201308*.shelf ../gliderModelGP2/
#rsync -avz -e "ssh -l resl" resl@cinaps.usc.edu:/mnt/data/storage/datasets/NoisyGliderModels/gliderModelGP2_201308*.shelf ../gliderModelGP2/
