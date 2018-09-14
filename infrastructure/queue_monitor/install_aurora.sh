#!/bin/bash
VERSION="aurora_linux_amd64_v2.1.tar.gz"
if [ ! -e aurora ] ;then
  wget https://github.com/Luxurioust/aurora/releases/download/2.1/$VERSION
  tar -zxvf $VERSION
  rm -f $VERSION
fi
