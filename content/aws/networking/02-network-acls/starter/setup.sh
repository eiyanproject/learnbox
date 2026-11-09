#!/usr/bin/env bash
# Networking 2: network ACLs that deny.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

# 1. A network ACL named public.


# 2. Its inbound rules: 90 deny all from 198.51.100.0/24; 100 allow TCP 443;
#    110 allow TCP 22 from 203.0.113.0/24; 120 allow TCP 1024-65535.


# 3. Its outbound rules: 100 allow TCP 1024-65535; 110 allow TCP 443.


# 4. Associate it with public-a and public-b.

