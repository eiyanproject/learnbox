---
title: Peering and private DNS
summary: Connecting two VPCs - non-overlapping ranges, a peering connection, routes on both sides - and a private hosted zone so the app finds its database by name.
order: 4
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`PCX=$(aws ec2 create-vpc-peering-connection --vpc-id \"$VPC_ID\" --peer-vpc-id \"$DATA_VPC\" --query VpcPeeringConnection.VpcPeeringConnectionId --output text)`, then `aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id \"$PCX\"`."
  - "Routes go both ways: in lb-vpc's private route table, 10.1.0.0/16 via the peering connection (`--vpc-peering-connection-id \"$PCX\"`); in the data VPC's route table, 10.0.0.0/16 back."
  - "`aws route53 create-hosted-zone --name internal.example --caller-reference \"lb-$(date +%s)\" --vpc VPCRegion=us-east-1,VPCId=\"$VPC_ID\" --hosted-zone-config PrivateZone=true --query HostedZone.Id --output text`, then associate the data VPC with `aws route53 associate-vpc-with-hosted-zone`."
  - "A record: `aws route53 change-resource-record-sets --hosted-zone-id \"$ZONE\" --change-batch '{\"Changes\":[{\"Action\":\"UPSERT\",\"ResourceRecordSet\":{\"Name\":\"db.internal.example\",\"Type\":\"A\",\"TTL\":60,\"ResourceRecords\":[{\"Value\":\"10.1.11.10\"}]}}]}'`."
---

## VPC peering

A **peering connection** joins two VPCs - in the same account or another,
the same Region or another - so their instances talk over private
addresses, on the AWS network.

Three rules the exam loves:

- **No overlapping CIDR ranges.** 10.0.0.0/16 cannot peer with 10.0.0.0/16 -
  plan address space before you need it.
- **Not transitive.** If A peers with B and B with C, A cannot reach C
  through B. Each pair needs its own connection - which is why many VPCs
  usually means **Transit Gateway**, a hub that routes between all of them.
- **Routes on both sides.** The connection does nothing until each VPC's
  route tables send the other's range to it.

Peering has no hourly charge; traffic across AZs or Regions is billed as
usual. Security groups can reference groups in a peered VPC in the same
Region.

## Private DNS with Route 53

A **private hosted zone** holds DNS records that only the VPCs associated
with it can resolve. The app asks for `db.internal.example`; only your VPCs
get an answer. When the database moves, you change one record, not every
application's configuration.

The VPCs need `enableDnsSupport` and `enableDnsHostnames` on (both are on
by default for VPCs made by the console wizard; `enableDnsHostnames` is off
for CLI-made ones).

## Your task

A second VPC holds the data tier. On top of the foundations VPC (lb-vpc,
10.0.0.0/16), the script already creates **`data-vpc`** (10.1.0.0/16) with
a subnet **data-a** and a route table **data**, and gives lb-vpc's private
subnets a route table **private**. Add:

1. a **peering connection** between lb-vpc and data-vpc, **accepted**;
2. a route in **private** to 10.1.0.0/16 through it, and in **data** to
   10.0.0.0/16 through it;
3. **DNS hostnames on** for both VPCs;
4. a **private hosted zone** `internal.example` associated with **both VPCs**,
   with an **A record** `db.internal.example` -> **10.1.11.10**.
