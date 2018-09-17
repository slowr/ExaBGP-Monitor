#!/usr/bin/python
import traceback
from socketIO_client import SocketIO, BaseNamespace
import os

try:
    host = os.getenv('EXABGP_HOST', 'localhost:5000')

    with SocketIO('http://{}'.format(host), namespace=BaseNamespace, wait_for_connection=False) as sio:

        def on_msg(bgp_message):
            print('msg {}'.format(bgp_message))

        sio.on('exa_message', on_msg)

        prefixes = {'prefixes': ['0.0.0.0/0']}
        sio.emit('exa_subscribe', prefixes)

        sio.wait()
except KeyboardInterrupt:
    pass
except:
    traceback.print_exc()
