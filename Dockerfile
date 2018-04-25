FROM jfloff/alpine-python:2.7
MAINTAINER Dimitrios Mavrommatis <jim.mavrommatis@gmail.com>

WORKDIR /tmp

COPY . ./
RUN pip install --no-cache-dir -r requirements.txt

RUN git clone -b 3.4 https://github.com/Exa-Networks/exabgp 

ENV PATH /tmp/exabgp/bin:/tmp/exabgp/sbin:$PATH

EXPOSE 179
EXPOSE 5000

RUN exabgp --fi > exabgp/etc/exabgp/exabgp.env
RUN sed -i 's?/usr/bin/python3?'`which python`'?' server.py

ENTRYPOINT ["/usr/bin/dumb-init", "bash", "entrypoint.sh"]