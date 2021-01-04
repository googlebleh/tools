#!/bin/bash

amixer set Master mute

# wait for advertisement to finish
while xdotool search --name "Advertisement"; do
  sleep 2
done

amixer set Master unmute

# in case this script is bound to Super+<some-key>
if [ "$DESKTOP_SESSION" = "xubuntu" ]; then
  # close the whisker menu
  xfce4-popup-whiskermenu -p
fi
