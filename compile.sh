#!/bin/bash

pyinstaller xdskappa.py --clean -y

cd dist
tar czvf ../release/xdskappa.tar.gz xdskappa/*

