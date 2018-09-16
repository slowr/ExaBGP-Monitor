#!/usr/bin/python
import traceback
from socketIO_client import SocketIO
import os

host = os.getenv('EXABGP_HOST', 'localhost:5000')

class ExaBGP():


    def __init__(self, prefixes, host):
        self.config = {}
        self.config['host'] = host
        self.config['prefixes'] = prefixes


    def start(self):
        while True:
            with SocketIO('http://' + self.config['host']) as sio:


                def on_msg(bgp_message):
                    print('msg {}'.format(bgp_message))


                def on_disconnect():
                    print('disconnect')
                    sio.disconnect()


                sio.on('connect', on_connect)
                sio.on('exa_message', on_msg)
                sio.on('disconnect', on_disconnect)

                prefixes_ = {'prefixes': self.config['prefixes']}
                sio.emit('exa_subscribe', prefixes_)

                sio.wait()

try:
    exa = ExaBGP(['0.0.0.0/0'], host)
    exa.start()
except KeyboardInterrupt:
    sio.disconnect()
except:
    traceback.print_exc()
