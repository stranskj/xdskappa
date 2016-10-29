#!/bin/bash

pyi-build xdskappa.spec --clean 

cd dist
mv xdskappa.show_stat/xdskappa.show_stat
mv xdskappa.run_xds/xdskappa.run_xds

#tar czvf ../release/xdskappa-v0.2.2-debian.tar.gz xdskappa/*

#rm -rf xdskappa

