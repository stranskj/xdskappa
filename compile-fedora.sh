#!/bin/bash

docker run -t -v /home/stransky/skripty/xdskappa:/src/xdskappa --user=$UID fedora:pyinst2 /bin/bash -c "cd /src/xdskappa; ./compile-dist.sh"
