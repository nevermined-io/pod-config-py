FROM python:3.8-slim-buster
LABEL maintainer="Keyko <root@keyko.io>"

ARG VERSION

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean

COPY . /nevermined-pod-config
WORKDIR /nevermined-pod-config

RUN pip install .
RUN pip install contracts-lib-py==0.4.0

ENTRYPOINT pod-config --help
