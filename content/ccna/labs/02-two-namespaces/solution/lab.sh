#!/bin/bash
ip link add veth0 type veth peer name veth1

# A second namespace, kept alive by a sleeping process.
unshare -n sleep 60 >/dev/null 2>&1 &
peer=$!
sleep 0.3

# veth1 leaves this namespace for the peer's.
ip link set veth1 netns "$peer"

ip addr add 10.1.1.1/24 dev veth0
ip link set veth0 up

nsenter -t "$peer" -n ip addr add 10.1.1.2/24 dev veth1
nsenter -t "$peer" -n ip link set veth1 up
nsenter -t "$peer" -n ip link set lo up
