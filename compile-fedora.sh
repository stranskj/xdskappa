#!/bin/bash

bash compile.sh

cd dist
tar czvf ../release/xdskappa-v0.2.3.2-fedora23.tar.gz xdskappa/*

rm -rf xdskappa

rm -rf *
