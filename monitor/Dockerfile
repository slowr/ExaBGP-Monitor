FROM mavromat/alpine-python:2.7
MAINTAINER Dimitrios Mavrommatis <jim.mavrommatis@gmail.com>

WORKDIR /home

RUN mkdir -p /usr/lib/python2.7.14/bin/
RUN ln -s /usr/local/lib/pyenv/versions/2.7.15/bin/python /usr/lib/python2.7.14/bin/python
RUN mkdir config
RUN mkdir exabgp
COPY requirements.txt ./
COPY server.py ./
COPY exabgp.conf ./config/
COPY exabgp/ ./exabgp/
COPY entrypoint.sh ./

RUN apk update && apk add --no-cache openssl-dev libffi-dev py-openssl
RUN pip install --no-cache-dir -r requirements.txt

ENV PATH /home/exabgp/bin:/home/exabgp/sbin:$PATH

EXPOSE 179
EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
