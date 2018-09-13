#!/bin/ash

echo "Starting zebra daemon..."
/usr/sbin/zebra -d -f /etc/quagga/zebra.conf
echo "Starting bgpd daemon..."
/usr/sbin/bgpd -f /etc/quagga/bgpd.conf
