#!/usr/bin/env bash
# Containers 4: Route 53 routing.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

# 1. Public hosted zone example.com.


# 2. Health check: HTTPS 192.0.2.10:443 /health, 30 s, 3 failures.


# 3. Failover app.example.com: primary 192.0.2.10 (health check),
#    secondary 198.51.100.10.


# 4. Weighted www.example.com: blue 192.0.2.20 (90), green 192.0.2.30 (10).


# 5. Latency api.example.com: us-east-1 192.0.2.40, eu-west-1 198.51.100.40.


# 6. Private zone internal.example.com for the VPC (DNS hostnames on), and
#    the CNAME db.internal.example.com.

