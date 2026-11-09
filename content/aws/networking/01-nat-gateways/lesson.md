---
title: NAT gateways, one per AZ
summary: Outbound internet for private subnets - an Elastic IP, a NAT gateway in each public subnet, and a private route table per Availability Zone so one AZ's failure stays in that AZ.
order: 1
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "A NAT gateway needs an Elastic IP: `EIP_A=$(aws ec2 allocate-address --domain vpc --query AllocationId --output text)`, then `aws ec2 create-nat-gateway --subnet-id \"$PUBLIC_A\" --allocation-id \"$EIP_A\" --query NatGateway.NatGatewayId --output text`."
  - "The NAT gateway goes in a PUBLIC subnet - it needs the internet gateway route to get out - and serves the PRIVATE subnet in the same AZ."
  - "One route table per private subnet: `create-route-table`, then `create-route --destination-cidr-block 0.0.0.0/0 --nat-gateway-id \"$NAT_A\"`, then `associate-route-table` with private-a. The same for b."
  - "Tag the route tables `private-a` and `private-b` with `--tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private-a}]'`."
---

Instances in private subnets often need to reach *out* - to download
updates, call a third-party API - while staying unreachable from the
internet. A **NAT gateway** does that: it sits in a public subnet with an
**Elastic IP** (a fixed public address), takes the private instances'
outbound connections and lets only the replies back in.

```
private instance  ->  private route table: 0.0.0.0/0 -> nat-...
nat gateway (in a public subnet)  ->  public route table: 0.0.0.0/0 -> igw-...
```

## One per AZ

A NAT gateway lives in one Availability Zone. If every private subnet uses
the NAT gateway in AZ a and AZ a fails, the instances in AZ b lose the
internet too - and in the meantime, every byte from b to the NAT gateway in
a is cross-AZ traffic, which is billed.

So the resilient pattern is **one NAT gateway per AZ**, and **one private
route table per AZ** pointing at the NAT gateway in the same AZ. (A single
shared NAT gateway is cheaper and fine for development - that trade-off is a
favourite exam question.)

NAT gateways are managed: AWS scales them (to 100 Gbps) and makes them
redundant *within* their AZ. A **NAT instance** - an EC2 instance doing the
same job - is cheaper at tiny scale and yours to patch, scale and fail over.

## Elastic IPs

`aws ec2 allocate-address --domain vpc` reserves a public IPv4 address for
the account until you release it. Public IPv4 addresses are charged by the
hour, attached or not, so release what you do not use.

## Your task

The script starts from the foundations VPC: `eval "$(awslab given vpc)"`
builds it and sets `VPC_ID`, `PUBLIC_A` and the rest. (`awslab given vpc
--show` prints the CLI commands it stands for.) Add:

1. a **NAT gateway in public-a** and one **in public-b**, each with its own
   Elastic IP;
2. a route table **`private-a`** sending 0.0.0.0/0 to the NAT gateway in
   **public-a**, associated with **private-a**;
3. the same for **`private-b`** and the NAT gateway in **public-b**.
