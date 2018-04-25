#!/bin/sh
if [[ "${LOCAL_IP}" ]]; then
    echo "Changing local IP to "${LOCAL_IP}
    sed -i "s/10.0.0.3/"${LOCAL_IP}"/" exabgp.conf
fi

if [[ "${REMOTE_IP}" ]]; then
    echo "Changing remote IP to "${REMOTE_IP}
    sed -i "s/10.0.0.1/"${REMOTE_IP}"/" exabgp.conf
fi

if [[ "${LOCAL_AS}" ]]; then
    echo "Changing local AS to "${LOCAL_AS}
    sed -i "s/65001/"${LOCAL_AS}"/" exabgp.conf
fi

if [[ ! -z "$@" ]]; then
    $@
else
    env exabgp.log.destination=/etc/exabgp/log exabgp.log.routes=true exabgp.daemon.user=root exabgp exabgp.conf
fi