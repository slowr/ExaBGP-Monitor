#!/usr/bin/python
import sys
import argparse
from sys import stdin
from flask import Flask, abort, request
from flask_socketio import SocketIO, send, emit
import json
import radix
import _thread
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
clients = {}
hostname = ''


def message_parser(line):
    try:
        temp_message = json.loads(line)
        if temp_message['type'] == 'update':
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
                    for sid in clients:
                        if clients[sid][0].search_best(prefix):
                            print('Sending to {} for {}'.format(sid, prefix))
                            emit('exa_message', message, room=sid)
    except:
        pass


def exabgp_update_event():
    while True:
        line = stdin.readline().strip()
        messages = message_parser(line)


@app.route('/')
def index():
    abort(404)


@socketio.on('connect')
def artemis_connect():
    print('Received connect..')
    emit('connect', room=request.sid)


@socketio.on('disconnect')
def artemis_disconnect():
    print('Received disconnect..')
    client = request.namespace
    sid = request.sid
    clients.pop(sid, None)


@socketio.on('exa_subscribe')
def artemis_exa_subscribe(message):
    sid = request.sid

    print('Received exa_subscribed from {}'.format(sid))
    all_prefixes = []
    try:
        prefix_tree = radix.Radix()
        for prefix in message['prefixes']:
            prefix_tree.add(prefix)
        clients[sid] = (prefix_tree, True)
    except:
        print('Invalid format received from %s'.format(sid))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ExaBGP Monitor Server')
    parser.add_argument('--name', type=str, dest='name', default='exabgp',
                        help='Hostname for ExaBGP monitor')
    args = parser.parse_args()

    hostname = args.name

    print('Starting Socket.IO server..')
    _thread.start_new_thread(lambda: socketio.run(app), ())
    exabgp_update_event()

