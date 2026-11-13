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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **isolated by default** | nothing in one VPC can reach another until they are connected |
| **peering connection** | joins two VPCs so they talk over private addresses, without the internet |
| **request** / **accept** | one side asks, the other VPC's owner accepts; until then `pending-acceptance` |
| **`active`** | the peering status once accepted |
| **overlapping ranges** | VPCs sharing addresses; they cannot peer |
| **transitive** | passing through: peering is not, so A-B and B-C does not connect A to C |
| **Transit Gateway** | a hub routing between many VPCs and networks |
| **return route** | the route for replies; needed on both sides |
| **edge-to-edge routing** | using a peer's internet gateway, NAT, VPN or endpoints; not allowed |
| **DNS** | the Domain Name System: programs ask for a name, it answers with the address |
| **Route 53** | AWS's DNS service |
| **hosted zone** | the DNS records for one domain |
| **private hosted zone** | records only the associated VPCs can look up |
| **associate** (a VPC) | let a VPC use a private hosted zone |
| **record** | a name, a type and a value |
| **A record** | maps a name to an IPv4 address |
| **TTL** | time to live: how many seconds a client may remember an answer |
| **change batch** | JSON listing record changes, each with an `Action` |
| **`UPSERT`** | create the record, or replace it if it exists |
| **caller reference** | a unique string per request, so a retry does not create two zones |
| **`enableDnsSupport`** / **`enableDnsHostnames`** | the VPC's resolver answers / instances get DNS names; the second is off for CLI-made VPCs |
| **Route 53 Resolver** | the VPC's DNS server, at its base address plus two |
| **Resolver inbound endpoint** | lets on-premises servers query it |
| **Site-to-Site VPN** | an encrypted link to an office over the internet, two tunnels |
| **Direct Connect** | a private line to AWS; not encrypted by default |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws ec2 create-vpc-peering-connection --vpc-id A --peer-vpc-id B` | requests peering |
| `aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id P` | accepts it |
| `aws ec2 create-route --route-table-id R --destination-cidr-block C --vpc-peering-connection-id P` | routes the other VPC's range through it |
| `aws ec2 describe-vpc-peering-connections` | shows peering status |
| `aws ec2 modify-vpc-attribute --vpc-id V --enable-dns-hostnames '{"Value":true}'` | turns on DNS hostnames |
| `aws ec2 describe-vpc-attribute --vpc-id V --attribute enableDnsHostnames` | shows it |
| `aws route53 create-hosted-zone --name N --caller-reference R --vpc VPCRegion=...,VPCId=... --hosted-zone-config PrivateZone=true` | creates a private zone |
| `aws route53 associate-vpc-with-hosted-zone --hosted-zone-id Z --vpc ...` | adds another VPC |
| `aws route53 change-resource-record-sets --hosted-zone-id Z --change-batch file://...` | creates or changes records |
| `aws route53 list-resource-record-sets --hosted-zone-id Z` | lists the records |
| `$(date +%s)` | the current time in seconds |
| `dig NAME` | looks a name up (on a real instance) |

---

Companies rarely have just one VPC. The data team's databases sit in their
own VPC, a partner runs another, each environment (development, production)
has its own. A VPC is isolated by default: nothing in one can reach the
other, even in the same account. When the application in `lb-vpc` needs the
database in `data-vpc`, the two have to be **connected**, and the
application needs a way to **find** the database that does not break when
its address changes. This lesson does both:

```text
 lb-vpc 10.0.0.0/16                              data-vpc 10.1.0.0/16
 ┌──────────────────────┐   peering connection   ┌──────────────────────┐
 │ private subnets      │ <────── pcx-... ─────> │ data-a 10.1.11.0/24   │
 │ route: 10.1.0.0/16   │                        │ route: 10.0.0.0/16    │
 │        -> pcx-...    │                        │        -> pcx-...     │
 └──────────────────────┘                        │ database 10.1.11.10   │
                                                 └──────────────────────┘
 private DNS zone internal.example (both VPCs):  db.internal.example -> 10.1.11.10
```

## VPC peering

A **peering connection** joins two VPCs, in the same account or different
ones, in the same Region or different ones, so that their instances talk to
each other over private addresses, on AWS's own network, without the
internet.

It is a request and an answer: one side **requests** the connection, and
the owner of the other VPC **accepts** it. Until then its status is
`pending-acceptance` (the emulator says `initiating-request`) and no traffic
flows. Both VPCs are yours here, so you accept it yourself.

Three rules the exam loves:

- **No overlapping CIDR ranges.** `10.0.0.0/16` cannot peer with
  `10.0.0.0/16`: if both sides have an address `10.0.1.5`, a route could not
  say which one it means. Real AWS refuses the request (the emulator is
  more forgiving). Plan address space before you need it, as Foundations
  lesson 7 advised.
- **Not transitive.** If A peers with B, and B with C, A still cannot reach
  C through B. Each pair that must talk needs its own connection. With many
  VPCs that becomes a tangle (10 VPCs, 45 connections), which is why larger
  setups use a **Transit Gateway**, a hub that routes between all the VPCs
  attached to it.
- **Routes on both sides.** The connection does nothing until each VPC's
  route tables send the **other** VPC's range to it. Traffic going there
  needs a route, and so do the replies coming back. Forgetting the return
  route is the classic mistake: requests leave, replies have nowhere to go.

💸 Peering has no hourly charge; traffic between AZs or Regions is billed as
usual. Security groups in one VPC can refer to groups in a peered VPC in the
same Region, as in Foundations lesson 8.

## Private DNS with Route 53

The application could use the database's address, `10.1.11.10`, directly.
But when the database is moved or replaced, its address changes, and every
application's configuration has to change with it. **DNS** (the Domain Name
System) solves this the way it does on the internet: programs ask for a
**name**, and DNS answers with the current address.

**Route 53** is AWS's DNS service. A **hosted zone** is a collection of DNS
records for one domain, such as `internal.example`. A **private hosted
zone** holds records that only the VPCs **associated** with it can look up;
nobody on the internet can see them. The application asks for
`db.internal.example`, and only your VPCs get the answer.

A record has a **name**, a **type** and a **value**. An **A record** maps a
name to an IPv4 address. Its **TTL** (time to live, in seconds) says how
long a client may remember the answer before asking again; a short TTL such
as 60 means a change reaches clients within a minute.

Records are changed with a **change batch**: a JSON document listing
changes, each with an `Action`. `UPSERT` means "create the record, or
replace it if it exists", so the same script can run twice:

```json
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "db.internal.example", "Type": "A", "TTL": 60,
      "ResourceRecords": [{"Value": "10.1.11.10"}]
    }
  }]
}
```

### Creating the zone

```
ZONE=$(aws route53 create-hosted-zone --name internal.example \
  --caller-reference "lb-$(date +%s)" \
  --vpc "VPCRegion=us-east-1,VPCId=$VPC_ID" \
  --hosted-zone-config PrivateZone=true \
  --query HostedZone.Id --output text)
```

- `--caller-reference` is a unique string per request, so that a request
  retried after a network glitch does not create two zones. `$(date +%s)`,
  the current time in seconds, makes a new one each run.
- A private zone must be created with one VPC (`--vpc`); more are added
  with `associate-vpc-with-hosted-zone`.
- The ID comes back as `/hostedzone/E49GPUGJ2S7GY1OWNI38TE`, with the prefix,
  which the other Route 53 commands accept as it is.

### VPC DNS settings

Two VPC attributes control DNS inside a VPC: `enableDnsSupport` (the VPC's
own DNS resolver answers queries; on by default) and `enableDnsHostnames`
(instances get DNS names, needed for private hosted zones to work). The
second is **on** for VPCs made by the console's wizard and **off** for VPCs
made with the CLI:

```
$ aws ec2 describe-vpc-attribute --vpc-id "$DATA_VPC" --attribute enableDnsHostnames
{
    "EnableDnsHostnames": {
        "Value": false
    },
    ...
}
```

Turn it on with `aws ec2 modify-vpc-attribute --vpc-id ...
--enable-dns-hostnames '{"Value":true}'`, one attribute per call.

## Choosing a connection

Peering has one more rule: **no edge-to-edge routing**. A VPC cannot use its
peer's internet gateway, NAT gateway, VPN, Direct Connect or gateway
endpoints; peering connects the two networks' own addresses only.

| Option | Use when | Key limits |
|---|---|---|
| **VPC peering** | a few VPCs, high traffic, lowest cost | non-transitive; no overlapping ranges; routes on both sides |
| **Transit Gateway** | many VPCs and on-premises networks | billed per attachment-hour and per GB; you add the VPC routes yourself |
| **PrivateLink** | expose **one service**, not a whole network | one-way; overlap allowed (lesson 3) |
| **Site-to-Site VPN** | a quick, encrypted link to an office | runs over the internet, two tunnels |
| **Direct Connect** | steady high bandwidth, predictable latency | weeks to set up; **not encrypted** by default |

Inside every VPC, the **Route 53 Resolver** answers DNS queries at the VPC's
base address plus two (`10.0.0.2` here). It is what consults the private
hosted zones associated with the VPC; on-premises servers cannot query it
directly and use a **Resolver inbound endpoint** instead.

## Your task

A second VPC holds the data tier. On top of the Foundations VPC (`lb-vpc`,
`10.0.0.0/16`), the script already creates **`data-vpc`** (`10.1.0.0/16`,
in `DATA_VPC`) with a subnet **`data-a`** and a route table **`data`** (in
`DATA_RT`), and gives lb-vpc's private subnets a route table **`private`**
(in `PRIVATE_RT`). Add:

1. a **peering connection** between lb-vpc and data-vpc, **accepted**, so
   its status is `active`;
2. a route in **`private`** for `10.1.0.0/16` through the peering
   connection, and in **`data`** for `10.0.0.0/16` through it (both
   directions);
3. **DNS hostnames on** for both VPCs;
4. a **private** hosted zone **`internal.example`** associated with **both
   VPCs**, with an **A record** `db.internal.example` pointing to
   **`10.1.11.10`**.

After **Run**, `aws ec2 describe-vpc-peering-connections --query
'VpcPeeringConnections[].[VpcPeeringConnectionId,Status.Code]'` should
show the connection `active`, and `aws route53 list-resource-record-sets
--hosted-zone-id "<zone id>"` the record. (The emulator has no running
resolver, so `db.internal.example` cannot actually be looked up here; in a
real VPC, `dig db.internal.example` on an instance would answer
`10.1.11.10`.)

## Check yourself

1. A peers with B, and B with C. Can A reach C?
   *No: peering is not transitive. Add A-C peering, or use a Transit
   Gateway.*
2. The peering connection is active, with a route only in lb-vpc. Why do
   connections fail?
   *The replies have no route back from data-vpc.*
3. Can lb-vpc and a VPC also using 10.0.0.0/16 be peered?
   *No: overlapping ranges cannot be peered.*
4. Why use `db.internal.example` rather than `10.1.11.10` in the app's
   configuration?
   *When the database moves, one DNS record changes instead of every app.*
