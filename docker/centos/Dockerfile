FROM centos:7
MAINTAINER Jan Stransky <stransky@ibt.cas.cz>

ARG pyver=2.7.13

RUN yum upgrade -y && \
		yum install -y epel-release && \
		yum install -y python-pip tar wget gcc g++ make bzip2 git redhat-lsb-core
RUN cd /tmp && \
	wget https://www.python.org/ftp/python/$pyver/Python-$pyver.tar.xz  

RUN cd /tmp && tar xf Python-$pyver.tar.xz 

RUN cd /tmp/Python-$pyver && \
	./configure && \
	make -j8 && \
	make install 

RUN cd / && rm -rf /tmp/Python-$pyver && \
	rm -rf /tmp/Python-$pyver.tar.xz

RUN pip install --upgrade pip && \
	pip install -I pyinstaller==2.1


RUN adduser stransky

USER stransky
