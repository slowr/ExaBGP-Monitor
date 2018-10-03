# ExaBGP-Monitor

An ExaBGP Control Plane monitor that connects with a BGP Speaker and has a Socket.IO interface to propagate all control-plane messages.

You need to provide the local ip address, the ip address of the BGP Speaker and the AS Number through the enviroment variables.

## ExaBGP Configuration

You can provide your own ExaBGP configuration by mounting the configuration file to /home/config/exabgp.conf.

Use the sample exabgp.conf for example and look into ExaBGP configuration for more details.

## Example

`docker run -v $(pwd)/exabgp.conf:/home/config/exabgp.conf mavromat/exabgp-monitor`

This will set a container with port 5000 exposed that you can connect with Socket.IO clients and retrieve the Control Plane BGP messages.

## Socket.IO Events/Messages

To Subscribe to the ExaBGP monitor:
```
Event: exa_subscribe
Message: prefixes as a list (e.g. ['10.0.0.0/8', '20.0.0.0/8'])
```

Messages sent from ExaBGP monitor to the socket.io client/subscriber:
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
