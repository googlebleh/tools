#!/bin/bash

# toggle touchpad status

device="AlpsPS/2 ALPS GlidePoint"
enabled=$(xinput --list-props "$device" | grep "Device Enabled" | awk '{print $NF}')

if [[ "$enabled" == "1" ]]; then
    xinput --disable "$device"
else
    xinput --enable "$device"
fi

if [ "$DESKTOP_SESSION" = "xfce" ]; then
    # in case this script is bound to a combo of Super+somekey XFCE will still
    # recognize the Super as a single button press so close the whisker menu
    # back
    xfce4-popup-whiskermenu
fi
