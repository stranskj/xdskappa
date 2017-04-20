#!/bin/bash

here=`pwd`

docker run -t -v $here:/src/xdskappa --user=$UID centos:pyinst2 /bin/bash -c "cd /src/xdskappa; ./compile.sh"
