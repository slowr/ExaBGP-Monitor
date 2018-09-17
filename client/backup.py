#!/usr/bin/python
from socketIO_client import SocketIO, BaseNamespace
import traceback
# import logging
# logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
# logging.basicConfig()

try:
    sio = SocketIO('localhost:5000')

    def on_msg(msg):
        pass

    sio.on('ris_rrc_list', on_msg)
    sio.wait()
except KeyboardInterrupt:
    sio.disconnect()
except Exception:
    traceback.print_exc()
