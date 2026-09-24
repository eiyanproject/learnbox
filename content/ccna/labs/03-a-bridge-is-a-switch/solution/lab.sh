#!/bin/bash
ip link add br0 type bridge
ip link set br0 up

for n in 1 2 3; do
    ip link add "h$n" type veth peer name "h${n}br"
    ip link set "h${n}br" master br0
    ip link set "h${n}br" up
    ip addr add "10.0.0.$n/24" dev "h$n"
    ip link set "h$n" up
done
