#!/bin/bash

pkill compton
# DISPLAY=:0.0 compton -b
DISPLAY=:0.0 /usr/local/bin/compton --config /home/cwee/repos/cwee-configs/xdg_config/compton/compton.conf -b
