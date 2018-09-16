#!/bin/sh

cat >bgpd.conf <<EOL
!
hostname bgp
password sdnip
!
!
router bgp ${AS_NUMBER}
    bgp router-id ${LOCAL_IP}

    ! announced networks
    network ${ANNOUNCED_PREFIX}

    ! timers
    timers bgp 1 3

    ! monitors
    neighbor ${NEIGHBOR_IP} remote-as ${NEIGHBOR_AS}
EOL

if [[ ! -z "${NEIGHBOR_IP2}" ]] && [[ ! -z "${NEIGHBOR_AS2}" ]]; then
cat >>bgpd.conf << EOL
    neighbor ${NEIGHBOR_IP2} remote-as ${NEIGHBOR_AS2}
EOL
fi

cat >>bgpd.conf << EOL
log stdout
EOL

echo "Starting zebra daemon..."
/usr/sbin/zebra -d -f /etc/quagga/zebra.conf
echo "Starting bgpd daemon..."
/usr/sbin/bgpd -f bgpd.conf
