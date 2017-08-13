#!/bin/bash

TPAD_CVAR="TouchpadOff"

# get current status
tpad_off=$( synclient -l | grep -E "$TPAD_CVAR\s+=" | cut -d '=' -f 2 )

# invert status and set result
synclient "$TPAD_CVAR=$((1 - tpad_off))"

if [ "$DESKTOP_SESSION" = "xubuntu" ]; then
  # close the whisker menu
  xfce4-popup-whiskermenu -p
fi
