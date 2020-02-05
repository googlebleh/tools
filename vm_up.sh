#!/bin/bash

set -ex

sudo apt install -y vim{,-gtk3} git tmux apt-file progress
sudo apt-file update

mkdir ~/repos
cd ~/repos
git clone --depth 1 https://github.com/googlebleh/cwee-configs.git
cd ~/repos/cwee-configs
./install.sh ~/repos/cwee-configs
