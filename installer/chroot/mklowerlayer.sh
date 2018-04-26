#!/bin/bash

releasever=27
packages="facter rubygem-json python3 hostname"

targetdir="$PWD/lower"
echo $targetdir
sudo dnf \
	-y \
	--disablerepo=adobe-linux-x86_64 \
	--disablerepo=google-chrome \
	--installroot=$targetdir \
	--releasever=$releasever \
	upgrade

sudo dnf \
	-y \
	--disablerepo=adobe-linux-x86_64 \
	--disablerepo=google-chrome \
	--installroot=$targetdir \
	--releasever=$releasever \
	install $packages

sudo dnf \
	-y \
	--disablerepo=adobe-linux-x86_64 \
	--disablerepo=google-chrome \
	--installroot=$targetdir \
	--releasever=$releasever \
	clean all
