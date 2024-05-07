#!/usr/bin/env bash

set -e

declare -a topleft_regexes=(
    "connected primary 3840x2160+0+0"
    "HDMI-1-0 connected 3840x2160+0+0"
    "DP-1-0 connected .\+3440x1440+0+0"
)

if xrandr | grep -q "${topleft_regexes[@]/#/--regexp=}"; then
    gtk_corner="top-left"
else
    gtk_corner="top-right"
fi

echo "Setting XFCE4 notify location to $gtk_corner"
xfconf-query -c xfce4-notifyd -p /notify-location -s "$gtk_corner"
