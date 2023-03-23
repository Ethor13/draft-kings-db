#!/bin/bash
cd tmp
rm -rf downloads
mkdir downloads
cd downloads
cat ../flags.csv | wc -l | awk '{print "Downloading " $1 " Files"}'
cat ../flags.csv | xargs -L 1 -P 10 wget --content-disposition -U
ls | wc -l | awk '{print "Downloaded " $1 " Files"}'
cd ../..
