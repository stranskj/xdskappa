#!/bin/bash
#run as root, or docker priviledged

docker run -t -v /home/stransky/skripty/xdskappa:/src/xdskappa fedora:pyinst2 /bin/bash -c "cd /src/xdskappa; ./compile-fedora.sh"
docker run -t -v /home/stransky/skripty/xdskappa:/src/xdskappa centos:pyinst2 /bin/bash -c "cd /src/xdskappa; ./compile-centos7.sh"
docker run -t -v /home/stransky/skripty/xdskappa:/src/xdskappa centos:pyinst2 /bin/bash -c "cd /src/xdskappa; chown -R stransky:users release"
chown -R stransky:users /home/stransky/skripty/xdskappa/release/

