#!/bin/bash

set -ex

sudo apt install -y vim{,-gtk3} git tmux

mkdir ~/repos
cd ~/repos
git clone --depth 1 https://github.com/googlebleh/cwee-configs.git
cd ~/repos/cwee-configs
./install.sh ~/repos/cwee-configs

echo "set completion-ignore-case On" >> ~/.inputrc
echo "set colored-completion-prefix On" >> ~/.inputrc
