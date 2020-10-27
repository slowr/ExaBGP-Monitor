#!/usr/bin/python
import argparse
from sys import stdin
from sys import stderr
from sys import stdout
from flask import Flask
import socketio
import json
import radix
import time
import traceback
import logging
from threading import Lock


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
lock = Lock()


def message_parser(line):
    try:
        temp_message = json.loads(line)
        if temp_message['type'] == 'update':
            log.debug('message: {}'.format(temp_message))

            update_msg = temp_message['neighbor']['message']['update']

            if 'announce' in update_msg:
                announce_msg = update_msg['announce']
                v4_origins = {}
                if 'ipv4 unicast' in announce_msg:
                    v4_origins = announce_msg['ipv4 unicast']
                v6_origins = {}
                if 'ipv6 unicast' in announce_msg:
                    v6_origins = announce_msg['ipv6 unicast']
                for origin in set(v4_origins.keys()).union(set(v6_origins.keys())):
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
                        prefixes = []
                        if origin in v4_origins:
                            prefixes.extend(v4_origins[origin])
                        if origin in v6_origins:
                            prefixes.extend(v6_origins[origin])
                        for prefix in prefixes:
                            message['prefix'] = prefix
                            lock.acquire()
                            try:
                                for sid, prefix_tree in clients.items():
                                    if prefix_tree.search_best(prefix):
                                        log.debug(
                                            'Sending to {} for {}'.format(
                                                sid, prefix))
                                        sio.emit('exa_message', message, room=sid)
                            except Exception:
                                log.exception('message exception')
                            finally:
                                lock.release()
            elif 'withdraw' in update_msg:
                withdraw_msg = update_msg['withdraw']
                message = {
                    'type': 'W',
                    'timestamp': temp_message['time'],
                    'peer_asn': temp_message['neighbor']['asn']['peer'],
                    'host': hostname
                }
                prefixes = []
                if 'ipv4 unicast' in withdraw_msg:
                    prefixes.extend(withdraw_msg['ipv4 unicast'])
                if 'ipv6 unicast' in withdraw_msg:
                    prefixes.extend(withdraw_msg['ipv6 unicast'])
                for prefix in prefixes:
                    message['prefix'] = prefix
                    lock.acquire()
                    try:
                        for sid, prefix_tree in clients.items():
                            if prefix_tree.search_best(prefix):
                                log.debug(
                                    'Sending to {} for {}'.format(
                                        sid, prefix))
                                sio.emit('exa_message', message, room=sid)
                    except Exception:
                        log.exception('message exception')
                    finally:
                        lock.release()
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
    lock.acquire()
    if sid in clients:
        del clients[sid]
    lock.release()


@sio.on('exa_subscribe')
def artemis_exa_subscribe(sid, message):
    log.info('exa_subscribe {}'.format(sid))
    try:
        prefix_tree = radix.Radix()
        for prefix in message['prefixes']:
            prefix_tree.add(prefix)
        lock.acquire()
        clients[sid] = prefix_tree
        lock.release()
    except BaseException:
        log.info(traceback.format_exc())
    log.info('subscribe {} for {}'.format(sid, message))


@sio.on("route_command")
def route_command(sid, message):
    log.info("route_command '{}' from {}".format(message["command"], sid))
    stderr.write(message["command"] + "\n")
    stderr.flush()
    stdout.write(message["command"] + "\n")
    stdout.flush()
    time.sleep(1)


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