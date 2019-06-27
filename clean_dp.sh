#!/bin/bash

# arc theme
autocfg_dim="Geometry: 596x197"
dispcfg_dim="Geometry: 587x435"

# adapta theme with Paper icons
# dispcfg_dim="Geometry: 589x447"

xdotool search --all --onlyvisible --name "Display" | while read win_id; do
    if xdotool getwindowgeometry "$win_id" | grep --quiet -e "$autocfg_dim" -e "$dispcfg_dim"; then
        xdotool key --window "$win_id" "Escape"  # close window
    else
        # xdotool windowactivate "$win_id"; sleep 3
        :
    fi
done

# in case this script is bound to Super+<some-key>
if [ "$DESKTOP_SESSION" = "xubuntu" ]; then
  # close the whisker menu
  xfce4-popup-whiskermenu -p
fi
