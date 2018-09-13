FROM jfloff/alpine-python:2.7
MAINTAINER Dimitrios Mavrommatis <jim.mavrommatis@gmail.com>

WORKDIR /home

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

RUN sed -i 's?/usr/bin/python?'`which python`'?' client.py

ENTRYPOINT ["./client.py"]
