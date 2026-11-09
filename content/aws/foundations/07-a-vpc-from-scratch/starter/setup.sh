#!/usr/bin/env bash
# Lesson 7: a VPC from scratch.
set -euo pipefail

# 1. The VPC lb-vpc, 10.0.0.0/16. Keep its ID: VPC_ID=$(aws ec2 create-vpc ...)


# 2. Four subnets: public-a 10.0.1.0/24 and private-a 10.0.11.0/24 in us-east-1a,
#    public-b 10.0.2.0/24 and private-b 10.0.12.0/24 in us-east-1b.


# 3. An internet gateway, attached to the VPC.


# 4. A route table named public: 0.0.0.0/0 to the internet gateway,
#    associated with public-a and public-b.


# 5. Public IPs on launch, for the public subnets only.

