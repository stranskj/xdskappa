FROM ubuntu:16.04
MAINTAINER Jan Stransky <stransky@ibt.cas.cz>

ARG pyver=2.7.15

RUN apt-get update && apt-get upgrade -y && \
		apt-get install -y tar bzip2 git lsb-release python python-dev

RUN apt-get install -y python-pip

# RUN pip install --upgrade pip && \
RUN pip install -I pyinstaller==2.1 

RUN adduser stransky

USER stransky
