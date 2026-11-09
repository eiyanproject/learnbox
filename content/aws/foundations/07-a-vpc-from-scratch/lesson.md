---
title: A VPC from scratch
summary: CIDR blocks, public and private subnets in two Availability Zones, an internet gateway, and the route table that makes a subnet public.
order: 7
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "Capture IDs as you go: `VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query Vpc.VpcId --output text)`. Every later command needs one."
  - "Names are tags: `--tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-a}]'` on create-subnet (ResourceType=vpc on create-vpc)."
  - "A subnet is public because of its route table, nothing else. Make one route table, add `--destination-cidr-block 0.0.0.0/0 --gateway-id \"$IGW_ID\"`, and associate it with public-a and public-b only. The private subnets keep the VPC's main route table."
  - "`aws ec2 modify-subnet-attribute --subnet-id \"$SUBNET\" --map-public-ip-on-launch` gives instances launched there a public IP."
---

A **VPC** (Virtual Private Cloud) is your own private network in a Region.
Everything with a network interface - instances, databases, load balancers,
Lambda functions that need private access - lives in a VPC.

## Addresses

A VPC gets an IPv4 range in **CIDR** notation. `10.0.0.0/16` means "the
first 16 bits are fixed": 10.0.0.0 to 10.0.255.255, 65,536 addresses. Use a
private range (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) and pick one that
will not overlap with your office or other VPCs - overlapping ranges cannot
be peered or connected later.

A **subnet** is a slice of the VPC's range in **one Availability Zone**.
`10.0.1.0/24` has 256 addresses, of which AWS reserves 5 (network,
router, DNS, future use, broadcast), leaving 251.

## Public and private

What makes a subnet **public** is one thing: its **route table** has a route
to an **internet gateway** (IGW).

| Route table | Destination | Target |
|---|---|---|
| public | 10.0.0.0/16 | local |
| public | 0.0.0.0/0 | igw-... |
| main (private) | 10.0.0.0/16 | local |

The `local` route is always there: every subnet in a VPC can reach every
other. A private subnet has no route to the internet at all; when its
instances need to reach out (for updates, say) they go through a **NAT
gateway** in a public subnet - a later lesson.

Each subnet is associated with exactly one route table. Subnets not
associated explicitly use the VPC's **main** route table - so leave the main
table private, and give public subnets their own.

## Two AZs, always

An AZ can fail. A design that has to survive it puts each tier in at least
two: a public and a private subnet in each of two AZs is the classic
starting shape.

## Your task

Build, in us-east-1:

| Name | What | CIDR | AZ |
|---|---|---|---|
| `lb-vpc` | VPC | 10.0.0.0/16 | |
| `public-a` | subnet | 10.0.1.0/24 | us-east-1a |
| `public-b` | subnet | 10.0.2.0/24 | us-east-1b |
| `private-a` | subnet | 10.0.11.0/24 | us-east-1a |
| `private-b` | subnet | 10.0.12.0/24 | us-east-1b |

with an **internet gateway** attached to the VPC, a **route table** named
**`public`** sending 0.0.0.0/0 to it, associated with **both public subnets
and neither private one**, and **public IPs on launch** for the public
subnets only. Names are `Name` tags.

`aws ec2 describe-route-tables --filters Name=vpc-id,Values=$VPC_ID` shows
the result - try `--output table`.
