#!/bin/bash

docker run -t -v `pwd`:/src/xdskappa --user=1001 ubuntu-16.04:pyinst2 /bin/bash -c "cd /src/xdskappa; ./compile-dist.sh"
