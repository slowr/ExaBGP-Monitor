#!/usr/bin/python
import sys
import argparse
from sys import stdin, stdout, stderr
from flask import Flask
import socketio
import json
import logging
import radix
import traceback
import logging


log = logging.getLogger('artemis')
log.setLevel(logging.INFO)
# create a file handler
handler = logging.FileHandler('/tmp/server.log')
handler.setLevel(logging.INFO)
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
            log.info('message: {}'.format(temp_message))
            log.info('clients: {}'.format(clients))
            for origin in temp_message['neighbor']['message']['update']['announce']['ipv4 unicast']:
                if 'as-path' in temp_message['neighbor']['message']['update']['attribute']:
                    message = {
                        'type': 'A',
                        'timestamp': temp_message['time'],
                        'peer': temp_message['neighbor']['ip'],
                        'host': hostname,
                        'path': temp_message['neighbor']['message']['update']['attribute']['as-path'],
                    }
                    for prefix in temp_message['neighbor']['message']['update']['announce']['ipv4 unicast'][origin]:
                        message['prefix'] = prefix
                        for sid, prefix_tree in clients.items():
                            if prefix_tree.search_best(prefix):
                                log.info('Sending to {} for {}'.format(sid, prefix))
                                sio.emit('exa_message', message, room=sid)
    except:
        log.info(traceback.format_exc())


def exabgp_update_event():
    while True:
        line = stdin.readline().strip()
        messages = message_parser(line)


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
    all_prefixes = []
    try:
        prefix_tree = radix.Radix()
        for prefix in message['prefixes']:
            prefix_tree.add(prefix)
        clients[sid] = prefix_tree
    except:
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
