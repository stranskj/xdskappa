#!/bin/bash

bash compile.sh

version=`git describe`
if [ $# -eq 1 ] ; then 
	dist=$1
else
	dist=`lsb_release -sri | sed 's/ //'`
fi

pathout="../release/xdskappa-$version-$dist.tar.gz"

echo "Version: $version"
echo "Linux version: $dist"

cd dist
tar czvf $pathout xdskappa/*

echo "Compressied binaries to: $pathout"
echo "Cleaning..."
rm -rf xdskappa

rm -rf *

echo "Done".
