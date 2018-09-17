#!/bin/sh
./wait-for exabgp:5000 -t 60
python client.py
