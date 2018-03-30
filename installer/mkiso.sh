#!/bin/bash

infilename='Fedora-Server-netinst-x86_64-27-1.6.iso'
outfilename="iWe-$infilename"
url="http://mirror.switch.ch/ftp/mirror/fedora/linux/releases/27/Server/x86_64/iso/$infilename"
builddir="$PWD/builder"

volumename='Fedora-S-dvd-x86_64-27' #xorriso -indev <iso file> 2>&1 | grep 'Volume id'

mntdir='/mnt/linux'

if [[ ! -f $infilename ]]; then
	wget $url
else
	echo
	echo $filename exists and I will not download it again
	echo
fi

sudo umount $mntdir
sudo mount -o loop $infilename $mntdir
if [[ $? != 0 ]]; then
	echo could not mount $filename $mntdir. Aborting...
	exit 1
fi

cd /mnt
tar -cvf - linux | (cd $builddir && tar -xf - )

cd $builddir/linux

xorriso -as mkisofs\
	-R\
	-J\
	-V $volumename\
	-o /tmp/$outfilename\
	-b isolinux/isolinux.bin\
	-c isolinux/boot.cat\
	-no-emul-boot\
	-boot-load-size 4\
	-boot-info-table\
	-eltorito-alt-boot\
	-e images/efiboot.img\
	-isohybrid-gpt-basdat\
	-no-emul-boot\
	-eltorito-alt-boot -e images/macboot.img\
	-no-emul-boot\
	-isohybrid-mbr /usr/share/syslinux/isohdpfx.bin\
	.

cd ../..
rm -f $outfilename
mv /tmp/$outfilename .

sudo umount $mntdir
