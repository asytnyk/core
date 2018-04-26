#!/bin/bash
IWEGARDE_CLIENT_SRC="/home/peter/dev/iwe/iwegarde-client"
DEST_DIR="upper/opt/iWe"
TOCP="activate_server.py requirements.txt start_activation.sh"

if [[ -f './merged/bin/bash' ]];then
	sudo umount merged
fi

for file in $TOCP; do
	cp -a $IWEGARDE_CLIENT_SRC/$file $DEST_DIR/
done
