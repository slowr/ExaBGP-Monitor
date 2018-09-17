#!/usr/bin/env bash
if [[ "${LOCAL_HOST}" ]]; then
    echo "Changing local IP to "${LOCAL_HOST}
    sed -i "s/10.0.0.3/"${LOCAL_HOST}"/" exabgp.conf
fi

if [[ "${REMOTE_HOST}" ]]; then
    echo "Changing remote IP to "${REMOTE_HOST}
    sed -i "s/10.0.0.1/"${REMOTE_HOST}"/" exabgp.conf
fi

if [[ "${LOCAL_AS}" ]]; then
    echo "Changing local AS to "${LOCAL_AS}
    sed -i "s/65001/"${LOCAL_AS}"/" exabgp.conf
fi

env exabgp.log.destination=/etc/exabgp/log exabgp.log.routes=true exabgp.daemon.user=root exabgp exabgp.conf
