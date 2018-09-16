#!/usr/bin/python
from __future__ import print_function
import sys
import argparse
from sys import stdin, stderr, exit
from flask import Flask, abort, request
from flask_socketio import SocketIO, emit
import json
import radix
import time
import thread


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
sio = SocketIO(app)
clients = {}
hostname = ''


def message_parser(line):
    try:
        temp_message = json.loads(line)
        if temp_message['type'] == 'update':
            print('message: {}'.format(temp_message))
            print('clients: {}'.format(clients))
            for origin in temp_message['neighbor']['message']['update']['announce']['ipv4 unicast']:
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
                            print('Sending to {} for {}'.format(sid, prefix))
                            emit('exa_message', message, room=sid)
    except:
        print(traceback.format_exc())


def exabgp_update_event():
    while True:
        line = stdin.readline().strip()
        messages = message_parser(line)


@sio.on('disconnect')
def sio_disconnect():
    print('disconnect')
    sid = request.sid
    clients.pop(sid, None)


@sio.on('exa_subscribe')
def sio_exa_subscribe(message):
    sid = request.sid

    print('exa_subscribe {}'.format(sid))
    all_prefixes = []
    try:
        prefix_tree = radix.Radix()
        for prefix in message['prefixes']:
            prefix_tree.add(prefix)
        clients[sid] = prefix_tree
    except:
        print('Invalid format received from %s'.format(sid))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ExaBGP Monitor Server')
    parser.add_argument('--name', type=str, dest='name', default='exabgp',
                        help='Hostname for ExaBGP monitor')
    args = parser.parse_args()

    hostname = args.name

    print('Starting Socket.IO server..')
    thread.start_new_thread(lambda: sio.run(app), ())
    exabgp_update_event()

