#!/bin/bash

docker run -t -v `pwd`:/src/xdskappa --user=1000 debian:pyinst2 /bin/bash -c "cd /src/xdskappa; ./compile-dist.sh Debian9.1"
