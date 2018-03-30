#!/bin/bash

infilename='Fedora-Server-netinst-x86_64-27-1.6.iso'
outfilename="iWe-$infilename"
url="http://mirror.switch.ch/ftp/mirror/fedora/linux/releases/27/Server/x86_64/iso/$infilename"
builddir="$PWD/builder"

volumename='Fedora-S-dvd-x86_64-27' #xorriso -indev <iso file> 2>&1 | grep 'Volume id'
mntdir='/mnt/linux'

# New partition is created for the user to save the installation key
extramegs=5

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
rm -rf $builddir/*
tar -cvf - linux | (cd $builddir && tar -xf - )

cd $builddir/..
rsync -vauz toadd/ $builddir/

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

# add a partition for the user to save the installation key
dd if=/dev/zero of=$outfilename bs=1M count=$extramegs oflag=append conv=notrunc

# From: https://superuser.com/questions/332252/how-to-create-and-format-a-partition-using-a-bash-script
# to create the partitions programatically (rather than manually)
# we're going to simulate the manual input to fdisk
# The sed script strips off all the comments so that we can 
# document what we're doing in-line with the actual commands
# Note that a blank line (commented as "defualt" will send a empty
# line terminated with a newline to take the fdisk default.
sed -e 's/\s*\([\+0-9a-zA-Z]*\).*/\1/' << EOF | fdisk $outfilename
  n # new partition
  p # primary partition
  4 # Partition number
    # default - start at beginning of disk 
    # default - end at the end of disk
  t # change partitio type
  4 # of partition 4
  c # to fat
  w # write the partition table
EOF

loopdev=$(sudo kpartx -av $outfilename|grep p4|cut -d ' ' -f 3)

sudo mkfs.vfat -n 'iWe' /dev/mapper/$loopdev

sudo kpartx -dv $outfilename


