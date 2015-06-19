#!/bin/sh
tar -xzvf mapready-3.2.1-src.tar.gz
cd /asf_tools
./configure
make
make install
cd /
rm -fr asf_tools
