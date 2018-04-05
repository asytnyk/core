#!/bin/bash

if [[ $1 == '' ]];then
	echo "Provide output file as an argument"
	echo "Something like ../toadd/linux/images/iwe.img"
	exit 1
fi
dest_file=$1

mount |grep "$PWD/merged"
if [[ "$?" != "0" ]];then
	echo "$PWD/merged does not seem to be mounted. Aborting..."
	exit 1
fi

if [[ -f "$dest_file" ]];then
	echo
	echo
	echo "$dest_file exists and will be removed. Press enter to continue"
	echo
	read
	sudo rm -f $dest_file
fi

sudo mksquashfs merged $dest_file -comp xz
