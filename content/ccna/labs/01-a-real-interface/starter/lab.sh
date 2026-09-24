#!/bin/bash
# Build the lab with ip commands. This runs inside your own network
# namespace as root - nothing here can affect the rest of the machine.
#
# Create a veth pair, address both ends in 10.1.1.0/24, and bring them up.

