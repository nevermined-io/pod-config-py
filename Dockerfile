FROM python:3.8-slim-buster
LABEL maintainer="Keyko <root@keyko.io>"

ARG VERSION

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean

COPY . /nevermined-pod-config
WORKDIR /nevermined-pod-config

RUN pip install pip==20.2.4
RUN pip install .

ENTRYPOINT pod-config --help
