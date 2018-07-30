FROM jfloff/alpine-python:2.7
MAINTAINER Dimitrios Mavrommatis <jim.mavrommatis@gmail.com>

WORKDIR /home

COPY . ./
RUN apk update && apk add --no-cache openssl-dev libffi-dev py-openssl
RUN pip install --no-cache-dir -r requirements.txt

RUN git clone -b 3.4 https://github.com/Exa-Networks/exabgp

ENV PATH /home/exabgp/bin:/home/exabgp/sbin:$PATH

EXPOSE 179
EXPOSE 5000

RUN exabgp --fi > exabgp/etc/exabgp/exabgp.env
RUN sed -i 's?/usr/bin/python3?'`which python`'?' server.py

ENTRYPOINT ["./entrypoint.sh"]
CMD ["env", "exabgp.log.destination=/etc/exabgp/log", "exabgp.log.routes=true", "exabgp.daemon.user=root", "exabgp", "exabgp.conf"]
