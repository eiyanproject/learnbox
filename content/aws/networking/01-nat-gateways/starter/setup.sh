#!/usr/bin/env bash
# Networking 1: NAT gateways, one per AZ.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

# 1. A NAT gateway in public-a and one in public-b, each with an Elastic IP.


# 2. Route table private-a: 0.0.0.0/0 to the NAT gateway in public-a,
#    associated with private-a.


# 3. Route table private-b: 0.0.0.0/0 to the NAT gateway in public-b,
#    associated with private-b.

