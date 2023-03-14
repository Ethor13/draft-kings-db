#!/bin/bash
cd tmp/downloads
if ls | grep .zip; then
    unzip -ov '*.zip' &> '../logs/unzip.log'
    rm -f *.zip &>> '../logs/unzip.log'
fi
echo "Downloads Formatted"
cd ../..