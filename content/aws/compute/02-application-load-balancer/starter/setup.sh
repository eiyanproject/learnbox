#!/usr/bin/env bash
# Compute 2: an Application Load Balancer.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

# 1. Security groups alb (80 and 443 from anywhere) and web (80 from alb only).


# 2. Target group web-tg: HTTP:80, instance targets, health check /health -> 200.


# 3. The internet-facing ALB web-alb in public-a and public-b, group alb.


# 4. An ACM certificate for www.example.com; HTTPS:443 forwarding to web-tg;
#    HTTP:80 redirecting to HTTPS with a 301.

