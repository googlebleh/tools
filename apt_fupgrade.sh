#!/bin/bash

set -ex

# var=0
# if []

sudo apt update
sudo apt -y upgrade
sudo apt -y autoremove

exit

upgradable=0
sudo apt update | while read line; do
  echo "$line"

  if [ "$upgradable" == 1 ]; then
    continue
  elif echo "$line" | grep -q "can be upgraded. Run 'apt list --upgradable' to see them."; then
    upgradable=0
  fi
done
