#!/usr/bin/env bash
sed -e "s/local-address\ [0-9.]*;/local-address\ $(ifconfig eth0 | awk '$1=="inet" {print $2}' | cut -d: -f2);/g" config/exabgp.conf > config/new.conf
exabgp --fi > exabgp/etc/exabgp/exabgp.env
env exabgp.log.destination=/etc/exabgp/log exabgp.log.routes=true exabgp.daemon.user=root exabgp /home/config/new.conf
