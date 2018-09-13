#!/usr/bin/python
import traceback
from socketIO_client import SocketIO

class ExaBGP():


    def __init__(self, prefixes, address, port):
        self.config = {}
        self.config['host'] = '{}:{}'.format(address, port)
        self.config['prefixes'] = prefixes


    def start(self):
        with SocketIO('http://' + self.config['host']) as socketIO:


            def on_connect(*args):
                print('on_connect')
                prefixes_ = {'prefixes': self.config['prefixes']}
                socketIO.emit('exa_subscribe', prefixes_)


            def on_pong(*args):
                print('on_pong {}'.format(args))


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
    traceback.print_exc()
