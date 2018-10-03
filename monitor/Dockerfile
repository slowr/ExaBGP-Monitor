FROM jfloff/alpine-python:2.7
MAINTAINER Dimitrios Mavrommatis <jim.mavrommatis@gmail.com>

WORKDIR /home

RUN mkdir config
RUN mkdir exabgp
COPY requirements.txt ./
COPY server.py ./
COPY exabgp.conf ./config/
COPY exabgp/ ./exabgp/

RUN apk update && apk add --no-cache openssl-dev libffi-dev py-openssl
RUN pip install --no-cache-dir -r requirements.txt

ENV PATH /home/exabgp/bin:/home/exabgp/sbin:$PATH
ENV exabgp.log.destination /etc/exabgp/log
ENV exabgp.log.routes=true
ENV exabgp.daemon.user=home

EXPOSE 179
EXPOSE 5000

RUN exabgp --fi > exabgp/etc/exabgp/exabgp.env

ENTRYPOINT ["exabgp", "/home/config/exabgp.conf"]
