#!/usr/bin/env bash

set -e

if [ "$#" -lt 2 ]; then
	echo "usage: $0 interface_name command [args...]"
	exit 1
fi

random_id ()
{
	tr -dc a-z </dev/urandom | head -c 10
}

iface="$1"
ip_addr=$(ip addr show dev "$iface" | awk '/inet / {print $2}')
if ! echo "$ip_addr" | grep -qF '/'; then
	echo "couldn't get IP range for $iface"
	exit 2
fi

macvlan_id="$(random_id)"
namespace_id="$(random_id)"

# create macvlan and put it inside a net namespace
sudo ip link add "$macvlan_id" link "$iface" type macvlan mode private
sudo ip netns add "$namespace_id"
sudo ip link set "$macvlan_id" netns "$namespace_id"

# assign macvlan iface to same IP range as host
sudo ip -n "$namespace_id" addr add "$ip_addr" dev "$macvlan_id"
sudo ip -n "$namespace_id" link set "$macvlan_id" up

# prep to run cleanup even if command fails
set +e

# run command
sudo ip netns exec "$namespace_id" sudo -u "$USER" "${@:2}"

# since macvlan iface is in netns, cleanup by deleting netns
sudo ip netns del "$namespace_id"
