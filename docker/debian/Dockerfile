FROM debian:jessie
MAINTAINER Jan Stransky <stransky@ibt.cas.cz>
RUN	apt-get update -y && \
	apt-get install -y python python-pip tar lsb-release git g++
RUN pip install --upgrade pip && \
	pip install -I pyinstaller==2.1
