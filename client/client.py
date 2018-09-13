#!/usr/bin/python
from socketIO_client import SocketIO

class ExaBGP():


    def __init__(self, prefixes, address, port):
        self.config = {}
        self.config['host'] = '{}:{}'.format(address, port)
        self.config['prefixes'] = prefixes


    def start(self):
        with SocketIO('http://' + self.config['host']) as socketIO:


            def on_connect():
                print('on_connect')
                # prefixes_ = {'prefixes': self.config['prefixes']}
                # socketIO.emit('exa_subscribe', prefixes_)

            def on_pong():
                print('on_pong')


            def exabgp_msg(bgp_message):
                print(msg)


            socketIO.on('connect', on_connect)
            socketIO.on('pong', on_pong)
            socketIO.on('exa_message', exabgp_msg)
            socketIO.wait()

try:
    exa = ExaBGP(['0.0.0.0/0'], 'localhost', 5000)
    exa.start()
except:
    pass
