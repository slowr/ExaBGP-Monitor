# ExaBGP Monitor with Socket.IO Server, Socket.IO Client and Quagga iBGP Peer

This repository contains three docker images:

i) An ExaBGP router with Socket.IO server embeded exposed on port 5000
ii) A python Socket.IO client that retrieves BGP update messages from the ExaBGP router in JSON format
iii) A Quagga BGP router

# Run

To run a simple test case use `docker-compose up` command

## Topology

    Socket.IO client <-- <BGP UPDATES> --> Socket.IO server / ExaBGP Monitor <-- <iBGP SESSION> --> QUAGGA1 <-- <eBGP SESSION> --> QUAGGA2

## Test behaviour
EXABGP creates an iBGP session with QUAGGA1

QUAGGA1 creates an eBGP session with QUAGGA2

Socket.IO client subscribes for 0.0.0.0/8 prefix to Socket.IO server

QUAGGA2 announces 2.0.0.0/8

QUAGGA1 announces 1.0.0.0/8

EXABGP receives announcements and forwards them to Socket.IO client
