#!/bin/bash

pyi-build xdskappa.spec --clean -y

cd dist
mv xdskappa.show_stat/xdskappa.show_stat xdskappa/
mv xdskappa.run_xds/xdskappa.run_xds xdskappa/

#tar czvf ../release/xdskappa-v0.2.2-debian.tar.gz xdskappa/*

#rm -rf xdskappa

