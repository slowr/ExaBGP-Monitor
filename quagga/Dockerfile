FROM alpine

MAINTAINER Dimitris Mavrommatis <jim.mavrommatis@gmail.com>

WORKDIR /home

COPY . ./

RUN apk add --no-cache quagga \
    && touch /etc/quagga/zebra.conf \
    && touch /etc/quagga/vtysh.conf

ENTRYPOINT ["./entrypoint.sh"]
