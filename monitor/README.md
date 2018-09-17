# ExaBGP-Monitor

An ExaBGP Control Plane monitor that connects with a BGP Speaker and has a Socket.IO interface to propagate all control-plane messages.

You need to provide the local ip address, the ip address of the BGP Speaker and the AS Number through the enviroment variables.

## Enviroment Variables

`LOCAL_IP` : Sets ExaBGP-Monitors local ip and also router id

`REMOTE_IP` : Sets Neighbors IP (BGP Speakers IP) to BGP the configuration

`LOCAL_AS` : Sets the AS in the BGP configuration (needs to be the same as the BGP Speakers to use iBGP)

## Example

docker run -e LOCAL_IP=10.0.0.1 -e REMOTE_IP=10.0.0.2 -e LOCAL_AS=65001 mavromat/exabgp-monitor

This will set a container with port 5000 exposed that you can connect with Socket.IO clients and retrieve the Control Plane BGP messages.

## Socket.IO Events

To Subscribe to the ExaBGP monitor:
```
Event: exa_subscribe
Message: prefix as string (e.g. '10.0.0.0/8')
```

Messages sent from ExaBGP monitor to the subscriber:
```
Event: exa_message
Message:
    'type': Type of the BGP message (Now it only sends BGP Update messages; you can change server.py to send also withdraw messages)
    'timestamp': Timestamp
    'peer': Peer of the BGP message
    'host': String identifier of the monitor (default 'exabgp')
    'path': BGP Update AS Path
    'prefix': Prefix that corresponds to the BGP Upate message
```
