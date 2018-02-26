#!/bin/bash

TMP="clientkeytmp"

if [[ ! $1 ]];then
	echo "Please provide commonName"
	exit
fi
commonName=$1

rm -rf $TMP
mkdir $TMP

cd easy-rsa
./easyrsa build-client-full $commonName nopass
if [[ $? != 0 ]];then
	echo "Something went wrong when generating the key"
	exit
fi
cp {./pki/private/$commonName.key,./pki/issued/$commonName.crt} ../$TMP/
cd ..

cp -P client/* $TMP/

cd $TMP
ln -sf $commonName.key client.key
ln -sf $commonName.crt client.crt
cd ..
