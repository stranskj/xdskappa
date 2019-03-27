#!/bin/bash

docker run -t -v `pwd`:/src/xdskappa --user=$UID debian:pyinst2 /bin/bash -c "cd /src/xdskappa; ./compile-dist.sh"
