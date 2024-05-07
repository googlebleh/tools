#!/usr/bin/env bash

rofi_single_click ()
{
  rofi \
    -dmenu \
    -l 30 \
    -i \
    -a 7 \
    -u 5 \
    -hover-select \
    -me-select-entry '' \
    -me-accept-entry MousePrimary \
    "$@"
}

export -f rofi_single_click
CM_LAUNCHER=rofi_single_click clipmenu
