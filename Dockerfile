FROM ryanmwhitephd/alpine-scipy-recordlinkage:73bdef0

MAINTAINER Dominic Parent <dominic.parent@canada.ca>

ADD linkage1.py ./linkage1.py
ADD funcs.py ./funcs.py
ADD cli_linkage.py ./cli_linkage.py

RUN pip3 install --upgrade pip
RUN pip install physt


