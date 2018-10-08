#!/usr/bin/python
import argparse
from sys import stdin
from flask import Flask
import socketio
import json
import radix
import traceback
import logging


log = logging.getLogger('artemis')
log.setLevel(logging.DEBUG)
# create a file handler
handler = logging.FileHandler('/tmp/server.log')
handler.setLevel(logging.DEBUG)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
log.addHandler(handler)

wz_log = logging.getLogger('werkzeug')
wz_log.setLevel(logging.ERROR)

async_mode = 'threading'
sio = socketio.Server(logger=False, async_mode=async_mode)
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
app.config['SECRET_KEY'] = 'secret!'

clients = {}
hostname = ''
thread = None


def message_parser(line):
    try:
        temp_message = json.loads(line)
        if temp_message['type'] == 'update':
            log.debug('message: {}'.format(temp_message))

            update_msg = temp_message['neighbor']['message']['update']

            if 'announce' in update_msg:
                announce_msg = update_msg['announce']
                for origin in announce_msg['ipv4 unicast']:
                    if 'as-path' in update_msg['attribute']:
                        communities = [{'asn': k[0], 'value': k[1]} for k in update_msg['attribute'].get('community', [])]
                        message = {
                            'type': 'A',
                            'timestamp': temp_message['time'],
                            'peer_asn': temp_message['neighbor']['asn']['peer'],
                            'host': hostname,
                            'path': update_msg['attribute']['as-path'],
                            'communities': communities
                        }
                        for prefix in announce_msg['ipv4 unicast'][origin]:
                            message['prefix'] = prefix
                            for sid, prefix_tree in clients.items():
                                if prefix_tree.search_best(prefix):
                                    log.debug(
                                        'Sending to {} for {}'.format(
                                            sid, prefix))
                                    sio.emit('exa_message', message, room=sid)
            elif 'withdraw' in update_msg:
                withdraw_msg = update_msg['withdraw']
                message = {
                    'type': 'W',
                    'timestamp': temp_message['time'],
                    'peer_asn': temp_message['neighbor']['asn']['peer'],
                    'host': hostname
                }
                for prefix in withdraw_msg['ipv4 unicast']:
                    message['prefix'] = prefix
                    for sid, prefix_tree in clients.items():
                        if prefix_tree.search_best(prefix):
                            log.debug(
                                'Sending to {} for {}'.format(
                                    sid, prefix))
                            sio.emit('exa_message', message, room=sid)
    except Exception:
        log.exception('message exception')


def exabgp_update_event():
    while True:
        line = stdin.readline().strip()
        message_parser(line)


@sio.on('connect')
def artemis_connect(sid, environ):
    log.info('connect {}'.format(sid))
    global thread
    if thread is None:
        thread = sio.start_background_task(exabgp_update_event)


@sio.on('disconnect')
def artemis_disconnect(sid):
    log.info('disconnect {}'.format(sid))
    if sid in clients:
        del clients[sid]


@sio.on('exa_subscribe')
def artemis_exa_subscribe(sid, message):
    log.info('exa_subscribe {}'.format(sid))
    try:
        prefix_tree = radix.Radix()
        for prefix in message['prefixes']:
            prefix_tree.add(prefix)
        clients[sid] = prefix_tree
    except BaseException:
        log.info(traceback.format_exc())
    log.info('subscribe {} for {}'.format(sid, message))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ExaBGP Monitor Server')
    parser.add_argument('--name', type=str, dest='name', default='exabgp',
                        help='Hostname for ExaBGP monitor')
    parser.add_argument('--ssl', dest='ssl', default=False,
                        help='Flag to use SSL', action='store_true')
    args = parser.parse_args()

    hostname = args.name
    ssl = args.ssl

    if ssl:
        log.info('Starting Socket.io SSL server..')
        app.run(ssl_context='adhoc', host='0.0.0.0')
    else:
        log.info('Starting Socket.io server..')
        app.run(host='0.0.0.0')
