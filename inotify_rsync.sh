#!/usr/bin/env bash

set -e

# usage: inotify_rsync.sh /project ssh_host:repos/project/

while inotifywait --event modify,create,delete,move --recursive "$1"; do
	rsync \
		--checksum \
		--cvs-exclude \
		--exclude=.git \
		--partial \
		--recursive \
		--rsh ssh \
		"$1" "$2"
done
