#!/bin/bash

wait_for_ssh ()
{
	local destination=$1
	local port=${2-22}

	while ! nc -w 2 $destination $port | grep -qP "^SSH"; do   
		sleep 2
	done
}
