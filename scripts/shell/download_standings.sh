#!/bin/bash
cd tmp
mkdir logs
mkdir downloads
cd downloads
ls ../urls | \
nl | \
awk '{print "-o ../logs/url_batch_" $1 ".log --input-file ../urls/" $2}' | \
xargs -L 1 -P 10 wget --content-disposition --load-cookies ../cookies.txt
cd ../..