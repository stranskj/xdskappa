#!/bin/bash

pyinstaller -p lib/ --clean -y bin/xdskappa.py bin/find.py

cd dist
tar czvf ../release/xdskappa-centos7.tar.gz xdskappa/*

