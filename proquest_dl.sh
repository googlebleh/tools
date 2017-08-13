#!/bin/bash

# cfg
main_wgeo="Geometry: 1920x1055"
main_wname="Practical Vim, 2nd Edition > Title Page : Safari Books Online - Google Chrome"

# assume script is run from a shell
my_wid=$(xdotool getwindowfocus)


# look for the matching window that isn't this window
main_wid=$(xdotool search --name "$main_wname" | grep -v "$my_wid")
if (( $(echo $main_wid | wc -l) != 1 )); then
    echo "Couldn't zoom in on Proquest window"
    exit 1
fi

