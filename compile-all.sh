#!/bin/bash
#run as root, or docker priviledged

./compile-fedora.sh
./compile-centos7.sh
#docker run -t -v /home/stransky/skripty/xdskappa:/src/xdskappa --user=$UID debian:pyinst2 /bin/bash -c "cd /src/xdskappa; ./compile-debian.sh"
chown -R stransky:users /home/stransky/skripty/xdskappa/release/

