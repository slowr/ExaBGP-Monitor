#!/usr/bin/python
import sys
import argparse
from sys import stdin, stderr, exit
from flask import Flask, abort, request
from flask_socketio import SocketIO, emit
import json
import radix
import time
import thread
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
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
sio = SocketIO(app)
clients = {}
hostname = ''


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
                                emit('exa_message', message, room=sid)
    except:
        log.info(traceback.format_exc())


def exabgp_update_event():
    try:
        while True:
            line = stdin.readline().strip()
            messages = message_parser(line)
    except KeyboardInterrupt:
        pass


@sio.on('connect')
def artemis_connect():
    sid = request.sid
    log.info('connect {}'.format(sid))


@sio.on('disconnect')
def sio_disconnect():
    sid = request.sid
    log.info('disconnect {}'.format(sid))
    clients.pop(sid, None)


@sio.on('exa_subscribe')
def sio_exa_subscribe(message):
    sid = request.sid
    log.info('exa_subscribe {}'.format(sid))
    all_prefixes = []
    try:
        prefix_tree = radix.Radix()
        for prefix in message['prefixes']:
            prefix_tree.add(prefix)
        clients[sid] = prefix_tree
    except:
        log.info('Invalid format received from %s'.format(sid))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ExaBGP Monitor Server')
    parser.add_argument('--name', type=str, dest='name', default='exabgp',
                        help='Hostname for ExaBGP monitor')
    args = parser.parse_args()

    hostname = args.name


    try:
        log.info('Starting Socket.IO server..')
        sio.start_background_task(exabgp_update_event)
        sio.run(app)
    except KeyboardInterrupt:
        pass

