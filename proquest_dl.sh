#!/bin/bash

set -e

myw_id=$(xdotool getwindowfocus) # assume script is run from a shell
curr_fname=77
end_title="Apply Customizations to Certain Types of Files"


# while (( $curr_fname < 3 )) ; do
while : ; do
    echo "Requesting print version of page $curr_fname"
    # mainw_geo="Geometry: 1920x1055"
    mainw_name="Practical Vim, 2nd Edition"
    mainw_but_x=284
    mainw_but_y=$((253-26))
    mainw_id=$(xdotool search --name "$mainw_name" | grep -v "$myw_id")
    if (( $(echo $mainw_id | wc -w) != 1 )); then
        echo "Couldn't zoom in on Proquest window"
        exit 1
    elif xdotool getwindowname "$mainw_id" | grep --quiet "$end_title"; then
        break  # done!
    fi
    xdotool windowraise "$mainw_id"
    sleep 0.5
    xdotool mousemove --window "$mainw_id" --sync "$mainw_but_x" "$mainw_but_y"
    xdotool click 1


    echo -n "  saving $curr_fname.pdf "
    # printw_geo="Geometry: 1920x1027"
    printw_name="proquest.safaribooksonline.com.proxy.library.cmu.edu/print"
    printw_but_x=290
    printw_but_y=$((170-26))
    printw_but_y=170
    printw_id=
    while : ; do
        printw_id=$(xdotool search --name "$printw_name" | grep -v "$myw_id" || true)
        if (( $(echo $printw_id | wc -w) == 1 )); then
            break
        elif (( $(echo $printw_id | wc -w) > 1 )); then
            echo "Couldn't zoom in on Print dialog"
            exit 1
        fi
    done
    sleep 0.5
    xdotool windowraise "$printw_id"
    xdotool windowfocus "$printw_id"
    # xdotool mousemove --window "$printw_id" --sync "$printw_but_x" "$printw_but_y"
    sleep 3  # print dialog can be a little slow
    # xdotool click 1
    xdotool key --window "$printw_id" "Return"

    echo "in default location"
    savew_name="Save File"
    savew_but_x=971
    savew_but_y=725
    savew_id=
    while : ; do
        savew_id=$(xdotool search --name "$savew_name" | grep -v "$myw_id" || true)
        if (( $(echo $savew_id | wc -w) == 1 )); then
            break
        elif (( $(echo $savew_id | wc -w) > 1 )); then
            echo "Couldn't zoom in on Save dialog"
            exit 1
        fi
    done
    xdotool windowraise "$savew_id"
    xdotool windowfocus "$savew_id"
    xdotool mousemove --window "$savew_id" --sync "$savew_but_x" "$savew_but_y"
    sleep 1
    xdotool key --window "$savew_id" $(echo $curr_fname | sed 's/./& /g')
    xdotool click 1
    sleep 0.2

    echo "  cleaning up print dialog"
    xdotool key --window "$printw_id" "alt+F4"
    sleep 0.5

    echo "Proceeding to next page"
    xdotool key --window "$mainw_id" n
    sleep 0.7

    (( curr_fname++ ))
    xdotool mousemove 40 40
    echo
done
