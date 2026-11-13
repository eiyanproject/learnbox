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

Servers, databases and load balancers need a network to live on, and you
want that network to be yours: your addresses, your rules about what can
reach what, and nothing else's traffic. A **VPC** (Virtual Private Cloud) is
such a private network inside one Region. Everything with a network
interface (instances, databases, load balancers, Lambda functions that need
private access) lives in a VPC.

This lesson builds the standard starting shape, which most of the rest of
the course builds on: a VPC with a **public** and a **private** subnet in
each of two Availability Zones, and a way out to the internet for the public
ones.

```text
 VPC lb-vpc 10.0.0.0/16 (us-east-1)
 ┌─────────────────────────────────────────────────────────────┐
 │  us-east-1a                     us-east-1b                  │
 │  ┌──────────────────────┐       ┌──────────────────────┐    │
 │  │ public-a 10.0.1.0/24 │       │ public-b 10.0.2.0/24 │ ───┼──> internet gateway ──> internet
 │  └──────────────────────┘       └──────────────────────┘    │      (via route table "public")
 │  ┌───────────────────────┐      ┌───────────────────────┐   │
 │  │ private-a 10.0.11.0/24│      │ private-b 10.0.12.0/24│   │   no route out
 │  └───────────────────────┘      └───────────────────────┘   │
 └─────────────────────────────────────────────────────────────┘
```

## Addresses: CIDR notation

Every device on the network needs an **IP address**. An IPv4 address is 32
bits, written as four numbers from 0 to 255 separated by dots, such as
`10.0.1.25`. A VPC is given a whole **range** of addresses, written in
**CIDR** notation (Classless Inter-Domain Routing): an address, a slash, and
how many of the leading bits are **fixed**.

`10.0.0.0/16` means "the first 16 bits are fixed at `10.0`; the other 16
are free". 16 free bits give 2^16 = 65,536 addresses, from `10.0.0.0` to
`10.0.255.255`. Each number between the dots is 8 bits, so:

| CIDR | Fixed part | Addresses | Range |
|---|---|---|---|
| `10.0.0.0/16` | `10.0` | 65,536 | 10.0.0.0 - 10.0.255.255 |
| `10.0.1.0/24` | `10.0.1` | 256 | 10.0.1.0 - 10.0.1.255 |
| `10.0.1.0/28` | first 28 bits | 16 | 10.0.1.0 - 10.0.1.15 |
| `0.0.0.0/0` | nothing | all of them | "anywhere": the whole internet |

A bigger number after the slash means a **smaller** range. A VPC can be
between `/16` and `/28`.

Use a **private** range, one reserved for private networks that the
internet never routes: `10.0.0.0/8`, `172.16.0.0/12` or `192.168.0.0/16`.
And pick one that will not **overlap** with your office network or your
other VPCs: two networks with overlapping ranges cannot be peered or
connected later (section 2). A VPC's first range is fixed for good (more
ranges can be added later, but never changed), so choose with room to grow.

## Subnets

A **subnet** is a slice of the VPC's range, in **one** Availability Zone.
Every resource is launched into a subnet, which is how you choose its AZ.
`10.0.1.0/24` has 256 addresses, of which AWS reserves 5 in every subnet
(the first four and the last: the network address, the VPC router, DNS, one
for future use, and broadcast), leaving 251 for you.

A subnet's range must lie inside the VPC's range, and must not overlap
another subnet's. The errors say which rule was broken:

```
An error occurred (InvalidSubnet.Conflict) when calling the CreateSubnet operation: The CIDR '10.0.1.0/24' conflicts with another subnet
An error occurred (InvalidSubnet.Range) when calling the CreateSubnet operation: The CIDR '10.1.0.0/24' is invalid.
```

(The second is outside `10.0.0.0/16`.)

## Public and private: it is the route table

An **internet gateway** (IGW) is the VPC's door to the internet: a
redundant, AWS-managed component you create and **attach** to the VPC. It
costs nothing and needs no sizing. But attaching it does not, by itself,
connect any subnet to it.

A **route table** decides where traffic leaving a subnet goes next. Each
**route** says "traffic for this destination range goes to this target",
and the most specific matching route wins. What makes a subnet **public**
is one thing, and only this: its route table has a route for `0.0.0.0/0`
(anywhere) to the internet gateway.

| Route table | Destination | Target | Meaning |
|---|---|---|---|
| public | 10.0.0.0/16 | local | other addresses in the VPC: deliver inside the VPC |
| public | 0.0.0.0/0 | igw-... | anything else: out through the internet gateway |
| main (private) | 10.0.0.0/16 | local | inside the VPC only; nothing else has anywhere to go |

The `local` route is always there and cannot be removed: every subnet in a
VPC can reach every other. A private subnet has no route to the internet
at all, so nothing in it can be reached from the internet, and nothing in it
can reach out either. When its instances do need to reach out (for software
updates, say) they go through a **NAT gateway** in a public subnet: section
2, lesson 1.

Each subnet is associated with exactly one route table. A subnet you do not
associate explicitly uses the VPC's **main** route table, which AWS creates
with the VPC. So leave the main table private, and give the public subnets
their own table: then a subnet someone adds later, and forgets to
associate, is private by default rather than accidentally public. The check
tests exactly this.

## Public IP addresses

A route to the internet is half of it: an instance also needs a **public**
IP address for the internet to reach it, since `10.0.1.25` means nothing
outside the VPC. A subnet attribute, **map public IP on launch**, gives
every instance launched there one automatically. It belongs on the public
subnets only.

## Two AZs, always

An Availability Zone can fail. A design that has to survive that puts each
tier in at least two AZs: a public and a private subnet in each of two AZs is
the classic starting shape, and the one built here.

## Working with the IDs

Every resource gets an ID when it is created (`vpc-...`, `subnet-...`,
`igw-...`, `rtb-...`), and later calls need those IDs. Capture each one into
a shell variable as it is created, as in lesson 3:

```
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=lb-vpc}]' \
  --query Vpc.VpcId --output text)
PUBLIC_A=$(aws ec2 create-subnet --vpc-id "$VPC_ID" --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-a}]' \
  --query Subnet.SubnetId --output text)
```

The **names** you see in the console are simply `Name` tags, set when the
resource is created with `--tag-specifications`; the `ResourceType` must
match what is being created (`vpc`, `subnet`, `internet-gateway`,
`route-table`). A small shell function saves writing it out each time:
`name() { echo "ResourceType=$1,Tags=[{Key=Name,Value=$2}]"; }`, then
`--tag-specifications "$(name subnet public-a)"`.

The remaining steps, in order:

1. `create-internet-gateway`, then `attach-internet-gateway` with the
   gateway's ID and the VPC's;
2. `create-route-table` in the VPC, then `create-route` on it for
   `0.0.0.0/0` with `--gateway-id` the internet gateway;
3. `associate-route-table` once for each public subnet;
4. `modify-subnet-attribute --map-public-ip-on-launch` for each public
   subnet.

## Three kinds of subnet, and a few rules

The route table decides more than public or private:

| Kind | Route table has | Reachable from the internet | Can reach the internet |
|---|---|---|---|
| **Public** | `0.0.0.0/0 -> igw-...` | yes, with a public IP and open firewalls | yes |
| **Private** | `0.0.0.0/0 -> nat-...` | no | outbound only (Networking lesson 1) |
| **Isolated** | `local` only | no | no |

Turning on "public IP on launch" does **not** make a subnet public; only the
internet gateway route does.

Some rules worth knowing early:

- A route table belongs to the VPC and is associated with **subnets**. It is
  never attached to an instance: an instance uses its subnet's table.
- When several routes match, the **longest prefix** (the most specific)
  wins, so `10.0.0.0/16 -> local` beats `0.0.0.0/0` for VPC addresses.
- A route whose target was deleted becomes a **blackhole**: traffic matching
  it is dropped.
- **Subnets cannot be resized**, and a VPC's first CIDR block cannot be
  changed. You can **add** secondary blocks to a VPC later, so start with a
  range big enough to grow into.
- The internet gateway translates addresses one to one: an instance's
  operating system only ever sees its **private** IP; the public one exists
  at the gateway.
- Every Region also has a **default VPC** (`172.31.0.0/16`, all subnets
  public), convenient for experiments and not meant for production.

## Your task

Build, in us-east-1:

| Name | What | CIDR | AZ |
|---|---|---|---|
| `lb-vpc` | VPC | 10.0.0.0/16 | |
| `public-a` | subnet | 10.0.1.0/24 | us-east-1a |
| `public-b` | subnet | 10.0.2.0/24 | us-east-1b |
| `private-a` | subnet | 10.0.11.0/24 | us-east-1a |
| `private-b` | subnet | 10.0.12.0/24 | us-east-1b |

with:

- an **internet gateway** attached to the VPC;
- a **route table** named **`public`**, with a route sending `0.0.0.0/0` to
  the internet gateway, associated with **both public subnets and neither
  private one**;
- the VPC's **main** route table left as it is, with no route to the
  internet, so the private subnets (which use it) stay private;
- **public IPs on launch** for the public subnets only.

Names are `Name` tags. After **Run**, look at the routing:

```
$ aws ec2 describe-route-tables --filters Name=vpc-id,Values=$VPC_ID --output table
```

(In the terminal `$VPC_ID` is not set; copy the VPC's ID from Run's output,
or look it up with `aws ec2 describe-vpcs --filters Name=tag:Name,Values=lb-vpc`.)
You should see two tables: the main one with only the `local` route, and
`public` with `local` and `0.0.0.0/0` to `igw-...`. Later lessons start from
this VPC with `eval "$(awslab given vpc)"`, which builds it and sets
`VPC_ID`, `PUBLIC_A` and the rest; `awslab given vpc --show` prints the
commands it stands for, which you can compare with yours.

## Check yourself

1. What makes a subnet public?
   *A route to an internet gateway in its route table, and nothing else.*
2. A new subnet nobody associated with a route table: public or private?
   *It uses the main route table, so it is private if the main table is.*
3. How many usable addresses are in a `/24` subnet, and why?
   *251: AWS reserves 5 in every subnet.*
4. Why plan VPC ranges that do not overlap?
   *Overlapping networks cannot be peered or connected later.*
5. Is a route table attached to an instance?
   *No: to subnets; instances use their subnet's table.*
