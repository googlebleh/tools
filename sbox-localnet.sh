#!/bin/bash

set -ex

group_name=sbox-localnet

if ! grep -q "${group_name}" /etc/group; then
  # create group to run processes as
  sudo addgroup "${group_name}"
fi

# drop all traffic
sudo iptables -I OUTPUT -m owner --gid-owner "${group_name}" -j DROP
# except that aimed at localhost: https://askubuntu.com/a/670412
# sudo iptables -I OUTPUT -d localhost -m owner --gid-owner "${group_name}" -j ACCEPT

# launch with
# sudo sg "${group_name}" -c "$(which ping) localhost"
