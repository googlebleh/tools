#!/bin/bash

set -e

sudo apt update
sudo apt -y full-upgrade
sudo apt -y autoremove
