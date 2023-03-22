#!/bin/bash
cd tmp
rm -rf downloads
mkdir downloads
cd downloads
cat ../flags.csv | \
xargs -L 1 -P 10 wget --content-disposition -U
echo "Downloads Complete"
cd ../..
