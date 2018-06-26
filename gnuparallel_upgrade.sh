#!/bin/bash

set -ex

# download and build latest release
wget http://ftp.gnu.org/gnu/parallel/parallel-latest.tar.bz2
tar xf parallel-latest.tar.bz2
parallel_dirs=( parallel-*/ )
latest_parallel="${parallel_dirs[-1]}"
cd "$latest_parallel"
./configure
make

# rm old version and install new one
if apt list parallel | grep -q "installed,local"; then
    sudo apt -y remove parallel
fi
sudo checkinstall --deldoc --delspec --deldesc --exclude=.

# cleanup
cd ..
rm -f parallel-*_built.tar.xz
tar cJf "${latest_parallel::-1}_built.tar.xz" "$latest_parallel"
rm -rf "$latest_parallel" parallel-latest.tar.bz2
