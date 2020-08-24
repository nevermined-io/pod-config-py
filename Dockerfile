FROM python:3.8-alpine
LABEL maintainer="Keyko <root@keyko.io>"

ARG VERSION

RUN apk add --no-cache --update \
    build-base \
    gcc \
    libffi-dev \
    openssl-dev

COPY . /nevermined-pod-config
WORKDIR /nevermined-pod-config

RUN pip install .
RUN pip install contracts-lib-py==0.4.0

ENTRYPOINT pod-config --help
