#!/bin/bash


bash compile.sh

cd dist
tar czvf ../release/xdskappa-v0.2.3.2-debian.tar.gz xdskappa/*

rm -rf *
