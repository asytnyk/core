#!/bin/bash

if [[ ! -f './merged/bin/bash' ]];then
	echo call mount.sh first
	exit
fi

sudo mount -o bind /dev merged/dev

sudo chroot merged
sudo rm -rf merged/root/{.bash_history,.cache}
sudo umount merged/dev
