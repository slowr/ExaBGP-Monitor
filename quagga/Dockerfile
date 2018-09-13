FROM alpine

MAINTAINER Dimitris Mavrommatis <jim.mavrommatis@gmail.com>

WORKDIR /root

COPY entrypoint.sh .
COPY bgpd.conf /etc/quagga/bgpd.conf

RUN apk add --no-cache quagga \
    && touch /etc/quagga/zebra.conf \
    && touch /etc/quagga/vtysh.conf

ENTRYPOINT ["./entrypoint.sh"]
