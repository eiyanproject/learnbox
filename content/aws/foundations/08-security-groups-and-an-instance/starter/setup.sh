#!/usr/bin/env bash
# Lesson 8: security groups and an instance.
set -euo pipefail

name() { echo "ResourceType=$1,Tags=[{Key=Name,Value=$2}]"; }

# ---- Done for you ----
# The VPC from lesson 7 (sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B)
# and the web-server role and instance profile from lesson 4.
# `awslab given vpc --show` prints the CLI commands they stand for.
eval "$(awslab given vpc)"
eval "$(awslab given web-server-role)"

# ---- This lesson ----

# 1. Security group web: 443 from anywhere, 22 only from 203.0.113.0/24.


# 2. Security group db: 5432 only from the web group.


# 3. The instance web: latest Amazon Linux 2023 (Parameter Store), t3.micro,
#    public-a, group web, instance profile web-server, IMDSv2 required.

