#!/bin/sh
rsync -avz -e "ssh -l ampereir" ampereir@asimov.usc.edu:~/RomsData/ ~/data/roms5/
