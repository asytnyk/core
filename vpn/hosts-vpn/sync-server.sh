#!/bin/bash

RFILE=/home/peter/vpn-conf.tar.gz

ssh vpn.iwe.cloud sudo rm -f $RFILE
ssh vpn.iwe.cloud sudo /usr/local/bin/collect-vpn.sh

scp vpn.iwe.cloud:/home/peter/vpn-conf.tar.gz /tmp

cd /home/peter/dev/iwe/vpn/hosts-vpn/server;

tar xzf /tmp/vpn-conf.tar.gz
rm /tmp/vpn-conf.tar.gz

ssh vpn.iwe.cloud sudo rm -f $RFILE
