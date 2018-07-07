#!/bin/bash
if [ ! -e aurora ] ;then
  wget https://github.com/Luxurioust/aurora/releases/download/2.0/aurora_linux_amd64_v2.0.tar.gz
  tar -zxvf aurora_linux_amd64_v2.0.tar.gz
  rm -f aurora_linux_amd64_v2.0.tar.gz
fi
