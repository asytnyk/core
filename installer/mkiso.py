#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests

# This is for future work when automation becomes important

mirror = 'http://mirror.switch.ch/ftp/mirror/fedora/linux/releases'
releasever = 27
url = "{}/{}/Server/x86_64/iso".format(mirror,releasever)
prefix = "Fedora-Server-netinst"
ext = "iso"

volume_name_cmd = [ xorriso -indev <file>|grep 'Volume id' ]

volume_name = 'Fedora-S-dvd-x86_64-27'
iso_path = '/tmp/out.iso'

mkisocmd = ['xorriso', '-as', 'mkisofs', '-R', '-J', '-V', volume_name, '-o',
        iso_path, '-b', 'isolinux/isolinux.bin', '-c', 'isolinux/boot.cat',
        '-no-emul-boot', '-boot-load-size', '4', '-boot-info-table',
        '-eltorito-alt-boot', '-e', 'images/efiboot.img',
        '-isohybrid-gpt-basdat', '-no-emul-boot', '-isohybrid-mbr',
        '/usr/share/syslinux/isohdpfx.bin']


def list_files(url, ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

def main():
    files = []
    for file in list_files(url, ext):
        if prefix in file and file not in files:
            files.append(file)
    print (files)

if __name__ == "__main__":
    main()
