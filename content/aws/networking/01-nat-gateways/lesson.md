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

Lesson 7 of Foundations left the private subnets with no route out at all.
That keeps them unreachable from the internet, which is the point, but
instances there often need to reach **out**: to download software updates,
or call a payment provider's API. They need outbound connections, while
still accepting no inbound ones.

**NAT** (network address translation) does exactly that. A **NAT gateway**
sits in a **public** subnet with a fixed public address. Private instances
send their outbound traffic to it; it forwards the traffic to the internet
under its own public address, and lets back in only the replies to
connections the instances opened. Nothing on the internet can start a
connection to them.

```text
 private instance 10.0.11.7
     │  private route table: 0.0.0.0/0 -> nat-...
     v
 NAT gateway (in public-a, public address 203.0.113.50)
     │  public route table: 0.0.0.0/0 -> igw-...
     v
 internet gateway -> internet      replies come back the same way; new inbound connections do not
```

Two route tables do the work: the private subnet's sends its default route
(`0.0.0.0/0`) to the NAT gateway, and the NAT gateway's own public subnet
sends its default route to the internet gateway. A NAT gateway in a
**private** subnet has no way out, which is why it must go in a public one.

## Elastic IPs

The NAT gateway's public address is an **Elastic IP**: a public IPv4 address
reserved for your account until you release it, so it does not change. That
matters when partners only accept traffic from known addresses: you can tell
them "our servers' traffic comes from 203.0.113.50".

```
$ aws ec2 allocate-address --domain vpc
{
    "AllocationId": "eipalloc-41b2f65d9d71152be",
    "Domain": "vpc",
    "PublicIp": "127.36.118.163"
}
```

The **allocation ID** is what other calls use to refer to it; capture it
with `--query AllocationId --output text`. (The emulator hands out odd
addresses such as `127.36...`; a real one is a normal public address.)

💸 Every public IPv4 address is charged by the hour, attached or not, so
release the ones you no longer use with `release-address`.

## One per AZ

A NAT gateway lives in **one** Availability Zone. Suppose both private
subnets use the NAT gateway in AZ a:

```text
 private-a ──> nat in a ──> internet
 private-b ──> nat in a ──> internet        AZ a fails: private-b loses the internet too
```

Two things go wrong. If AZ a fails, instances in AZ b lose the internet as
well, so a failure that should have stayed in one AZ spreads to both. And
even on a normal day, every byte from AZ b to the NAT gateway in AZ a is
**cross-AZ traffic**, which is billed.

So the resilient pattern is **one NAT gateway per AZ**, and **one private
route table per AZ** pointing at the NAT gateway in the **same** AZ:

```text
 private-a ──route table private-a──> nat in public-a ──> internet
 private-b ──route table private-b──> nat in public-b ──> internet
```

The trade-off is a favourite exam question. A single shared NAT gateway is
cheaper and fine for development; production that must survive an AZ
failure needs one per AZ.

💸 A NAT gateway is billed for every hour it exists and for every GB it
processes (in us-east-1 in 2025, about $0.045 for each, so roughly $32 a
month per gateway before any traffic). That makes it one of the classic
surprise bills: delete the ones you are not using. For traffic to S3 and
DynamoDB, a free gateway endpoint avoids the NAT gateway altogether (lesson
3).

A few more facts about NAT gateways:

- A NAT gateway has **no security group**; only the subnet's network ACL
  (lesson 2) filters its traffic, and it needs the ephemeral ports open.
- It handles 5 Gbps and scales automatically up to 100 Gbps.
- Only the VPC's own subnets can use it: traffic arriving through a peering
  connection (lesson 4), a VPN or Direct Connect cannot go out through it.

## NAT gateway or NAT instance

NAT gateways are **managed**: AWS scales them (up to 100 Gbps) and makes them
redundant **within** their AZ, and there is nothing to patch. A **NAT
instance**, an ordinary EC2 instance configured to do the same job, can be
cheaper at tiny scale, but it is yours to patch, size and fail over, and it
needs its *source/destination check* turned off. New designs use NAT
gateways.

## Newer options and real-world limits

- A **Regional NAT gateway** (introduced in November 2025) is one gateway
  for the whole VPC that spans its AZs by itself and needs no public subnet,
  with a single shared private route table. The one-per-AZ zonal design in
  this lesson is still the common one, and the one the exam has long asked
  about.
- A **private NAT gateway** has no Elastic IP; it translates traffic towards
  other private networks, typically when address ranges overlap.
- One NAT gateway address handles about 55,000 simultaneous connections to
  each destination; beyond that, connections fail (the metric
  `ErrorPortAllocation` shows it), and more Elastic IPs can be added. Idle
  connections are closed after 350 seconds.

### "My private instance can't reach the internet"

Check, in order:

1. the private subnet's route table has `0.0.0.0/0 -> nat-...`, and the
   route is active, not a blackhole;
2. the NAT gateway is `available`, sits in a **public** subnet, and has an
   Elastic IP;
3. the NAT gateway's public subnet routes `0.0.0.0/0` to the internet
   gateway;
4. the instance's security group allows the traffic out, and the network
   ACLs of both subnets allow it, ephemeral return ports included.

## Your task

The script starts from the Foundations VPC: `eval "$(awslab given vpc)"`
builds it and sets `VPC_ID`, `PUBLIC_A`, `PUBLIC_B`, `PRIVATE_A` and
`PRIVATE_B`. (`awslab given vpc --show` prints the CLI commands it stands
for.) Add:

1. a **NAT gateway in public-a** and one **in public-b**, each with its own
   Elastic IP, allocated with `allocate-address` and passed to
   `create-nat-gateway` as `--allocation-id`;
2. a route table named **`private-a`** with a route sending `0.0.0.0/0` to
   the NAT gateway in **public-a**, associated with the subnet
   **private-a**;
3. the same for **`private-b`** and the NAT gateway in **public-b**.

The check also makes sure the private subnets have no route to the
**internet gateway**, which would make them public. The two halves are the
same steps with different values, so a small shell function taking the
subnet and the name saves writing them twice, as in Foundations lesson 7.

After **Run**, `aws ec2 describe-nat-gateways --query
'NatGateways[].[NatGatewayId,SubnetId,State]' --output table` lists the two
gateways. In the emulator they are `available` at once; a real NAT gateway
spends a minute or two `pending` first.

## Check yourself

1. Why must a NAT gateway be in a public subnet?
   *It reaches the internet through the internet gateway route of its own
   subnet.*
2. Instances in AZ b use the NAT gateway in AZ a. Name two problems.
   *Cross-AZ data charges, and AZ a failing cuts AZ b off too.*
3. Can you put a security group on a NAT gateway?
   *No; only the network ACL of its subnet applies.*
4. Can anything on the internet open a connection to an instance behind a
   NAT gateway?
   *No: only replies to connections the instance opened come back.*
