FROM debian:jessie
MAINTAINER Jan Stransky <stransky@ibt.cas.cz>

ARG pyver=2.7.13

RUN apt-get update && apt-get upgrade -y && \
		apt-get install -y tar bzip2 git lsb-release python python-dev

RUN apt-get install -y python-pip

RUN pip install --upgrade pip && \
	pip install -I pyinstaller==2.1 

RUN adduser stransky

USER stransky
