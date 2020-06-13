#!/bin/bash

wait_for_ssh ()
{
	local destination=$1
	local timeout=${2-5}

	until timeout ${timeout} ssh ${destination} exit; do
		sleep 2
	done
}
