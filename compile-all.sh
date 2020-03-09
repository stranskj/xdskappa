#!/bin/bash
#run as root, or docker priviledged

#./compile-fedora.sh
./compile-centos7.sh
#./compile-debian.sh
chown -R stransky:users `pwd`/release/

