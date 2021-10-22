#!/bin/bash

# Print currently connected SSID

set -e


whichq ()
{
  which "$@" > /dev/null 2>&1
}


if whichq iwgetid; then
  iwgetid --raw

elif whichq iw; then
  iw dev wlp2s0 link | grep -Po 'SSID: \K.*'

elif whichq ip nmcli; then
  device=$(ip route | grep -Po "default.*dev \K\w+")
  nmcli -t connection show --active | grep -Fw "$device" | cut -d : -f 1

else
  >&2 echo "insufficient supported tools"
  exit 1
fi
