#!/bin/bash

docker run -t -v `pwd`:/src/xdskappa --user=1000 centos:pyinst2 /bin/bash -c "cd /src/xdskappa; ./compile-dist.sh"
