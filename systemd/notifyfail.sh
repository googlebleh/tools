#!/bin/bash

service_name="$1"
recipients=(
    "e@mail.com"
)

sendmail \
    -s "$(hostname): $service_name failed" \
    "${recipients[@]}" \
    < <(journalctl --no-pager -S today -u "$service_name.service")
