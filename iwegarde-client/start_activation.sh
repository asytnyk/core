#!/bin/sh

facter -j > /tmp/facter.json

source /opt/iWe/venv/bin/activate

mkdir -p /tmp/iWe/client-conf

/opt/iWe/activate_server.py /tmp/iWe/install_keys/iWe-install-key-*.json /tmp/facter.json
