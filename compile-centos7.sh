#!/bin/bash

bash compile.sh

cd dist
tar czvf ../release/xdskappa-v0.2.3-centos7.tar.gz xdskappa/*

rm -rf xdskappa

rm -rf *
