#!/bin/bash
# Build a three-port switch from a Linux bridge.
#
#   h1 ---- [ br0 ] ---- h2
#              |
#              h3
#
# The *br ends plug into the bridge and have no address;
# h1, h2 and h3 hold 10.0.0.1/24, .2/24 and .3/24.

