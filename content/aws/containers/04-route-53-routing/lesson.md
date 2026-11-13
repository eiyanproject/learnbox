---
title: Route 53 routing
summary: A public hosted zone with a health-checked failover pair, a weighted 90/10 canary, a latency-routed API in two Regions, and a private hosted zone that only the VPC can resolve.
order: 4
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`ZONE=$(aws route53 create-hosted-zone --name example.com --caller-reference \"$(date +%s)-pub\" --query HostedZone.Id --output text)`. Caller references must be unique per request."
  - "`aws route53 create-health-check --caller-reference \"$(date +%s)-hc\" --health-check-config IPAddress=192.0.2.10,Port=443,Type=HTTPS,ResourcePath=/health,RequestInterval=30,FailureThreshold=3 --query HealthCheck.Id --output text`."
  - "Record sets go in a change batch: write it with python3 and `aws route53 change-resource-record-sets --hosted-zone-id \"$ZONE\" --change-batch file://changes.json`. Failover, weighted and latency records all need a `SetIdentifier`; failover uses `\"Failover\": \"PRIMARY\"`, weighted `\"Weight\": 90`, latency `\"Region\": \"us-east-1\"`."
  - "A private zone is tied to a VPC at creation: `aws route53 create-hosted-zone --name internal.example.com --caller-reference ... --vpc VPCRegion=us-east-1,VPCId=$VPC_ID --hosted-zone-config PrivateZone=true`."
---

Computers connect to IP addresses; people type names. **DNS** (the Domain
Name System) turns `app.example.com` into `192.0.2.10`. It is also one of
the simplest places to **steer traffic**: send users to a standby site when
the main one is down, send 10% of them to a new version, or send each to the
nearest Region. **Route 53** is AWS's DNS service, and its routing policies
do all three. It is named after port 53, DNS's port, and is the only AWS
service with a 100% availability SLA.

```text
 public zone example.com (anyone on the internet can ask)
   app.example.com  failover   primary 192.0.2.10 (health check /health)  else  secondary 198.51.100.10
   www.example.com  weighted   blue 192.0.2.20 (90)   green 192.0.2.30 (10)
   api.example.com  latency    us-east-1 192.0.2.40   eu-west-1 198.51.100.40
 private zone internal.example.com (only the VPC can ask)
   db.internal.example.com  CNAME  orders.cluster-abc.us-east-1.rds.amazonaws.com
```

## How a lookup works

A browser asks a **resolver** (from the ISP, the company, or the VPC). If
the resolver has no cached answer, it asks the **root** servers, which point
it to the servers for `.com`, which point it to the **name servers** for
`example.com`, which give the answer. Those last servers are
**authoritative**: they hold the domain's records. Route 53 is
authoritative DNS, and also a **registrar** (where a domain is bought);
the two jobs are separate, and a domain bought elsewhere can use Route 53
by giving the registrar the four name servers of its hosted zone.

DNS only hands out an address. **Traffic never flows through Route 53**:
the client connects to the address itself.

## Hosted zones and records

A **hosted zone** holds the records for one domain and its subdomains (💸
$0.50 a month per zone). A **public** zone answers anyone on the internet;
a **private** zone, below, answers only your VPCs. Each new zone starts
with an `NS` record (its four name servers) and an `SOA` record.

A **record** has a name, a type, values, a TTL and a routing policy. The
types you meet most:

| Type | Maps a name to | Example |
|---|---|---|
| **A** | IPv4 addresses | `app.example.com` → `192.0.2.10` |
| **AAAA** | IPv6 addresses | `app.example.com` → `2001:db8::10` |
| **CNAME** | another name | `db.internal.example.com` → an RDS endpoint |
| **NS** | the zone's name servers | delegation |
| MX, TXT | mail servers; text (domain ownership proofs, SPF) | |

**TTL** (time to live) is how many seconds resolvers may cache an answer.
During that time they do not ask again, so a change, including a failover,
reaches a client only after its cached copy expires:

| TTL | Changes take effect | Cost |
|---|---|---|
| 60 s | within about a minute | more queries (💸 billed per million) |
| 86400 s (1 day) | up to a day later | fewer queries |

Lower a record's TTL **before** a planned change, wait for the old TTL to
pass, then change it. Records that steer traffic (this lesson's) use 60.

### Alias records

An **alias** is a Route 53 extension: an A or AAAA record whose target is
an AWS resource (ALB or NLB, CloudFront distribution, API Gateway, S3
website endpoint, VPC interface endpoint, Global Accelerator, or another
record in the zone) instead of a fixed address. Compared with a CNAME:

| | **CNAME** | **Alias** |
|---|---|---|
| Target | any name | AWS resources only (never an EC2 instance's DNS name) |
| At the zone apex (`example.com` itself) | **not allowed** | allowed |
| Queries | billed | free, for AWS targets |
| TTL | yours | Route 53's, from the target |
| Follows the target's IP changes | the client resolves again | yes |
| Health | no | `EvaluateTargetHealth` uses the target's health |

DNS forbids a CNAME next to other records with the same name, and the apex
always has NS and SOA, so `example.com → my-alb` must be an alias.
Load balancers have no fixed IPs (Compute lesson 2), so pointing an A record
at an ALB's current IP breaks when the IP changes; alias it instead.

## Routing policies

The **routing policy** decides which answer each query gets:

| Policy | Answers with | Exam wording |
|---|---|---|
| Simple | the record's values (all of them; the client picks) | one resource |
| **Failover** | the primary while its health check passes, otherwise the secondary | "active/passive", "automatic DR to a standby site" |
| **Weighted** | each record in proportion to its weight | "send 10% to the new version", canary, blue/green |
| **Latency** | the Region with the lowest measured latency from the user's resolver | "best performance for users worldwide", active/active |
| Geolocation | by the user's continent, country or US state | "French users see French content", block a country |
| Geoproximity | by distance, shifted by a **bias** | "gradually move users from one Region to another" |
| Multivalue | up to eight **healthy** records, chosen at random | simple client-side spreading (not a load balancer) |
| IP-based | by the resolver's IP range (CIDR) | known ISP or office networks |

Every record except simple ones carries a **`SetIdentifier`**, unique among
the records with the same name and type, so Route 53 can tell `blue` from
`green`. Details worth knowing:

- **Failover**: exactly one `PRIMARY` and one `SECONDARY`. The primary
  **must** have a health check (or be an alias with target health),
  otherwise Route 53 always considers it healthy and never fails over.
- **Weighted**: a record gets `weight / sum of weights` of the answers, so
  90 and 10 are 90% and 10%; weights need not add up to 100. Weight 0 sends
  nothing (unless all are 0). Moving the canary forward is changing two
  numbers.
- **Latency**: the `Region` field says where each endpoint is; Route 53
  uses its own latency measurements between networks and AWS Regions, not
  distance.
- **Geolocation**: add a **default** record, or users from places no
  record matches get no answer.

## Health checks

A **health check** probes an endpoint from about 15 checkers around the
world, over HTTP, HTTPS or TCP:

- every **30** seconds, or every 10 (💸 "fast", at extra cost);
- a check passes on a 2xx or 3xx status within the time limit;
- an endpoint becomes unhealthy after `FailureThreshold` consecutive
  failures (3 here: about 90 seconds), and is healthy while **more than
  18%** of checkers see it healthy.

❗ The checkers are **on the internet**: the endpoint's security group must
allow their IP ranges, and they can never reach a private subnet or an
on-premises server. For those, alarm on a CloudWatch metric and create a
health check that follows the **alarm**. **Calculated** checks combine
others (healthy if at least N of these are).

So a failover takes roughly: failure detection (3 × 30 s) plus the TTL
(60 s) for resolvers to ask again: two to three minutes.

## Private hosted zones

A **private** zone answers only queries that come from the VPCs
**associated** with it, through the VPC's own resolver (the `.2` address,
Networking lesson 1). Use it for internal names, like a stable
`db.internal.example.com` in front of a long RDS endpoint: when the database
moves, change one record instead of every application's configuration.

- The VPC needs both `enableDnsSupport` (on by default) and
  **`enableDnsHostnames`** (off by default in VPCs you create).
- A private zone is associated with a VPC when it is created (`--vpc`); more
  VPCs, even in other accounts, can be associated later.
- A private zone with the **same name** as a public one hides the public
  records from those VPCs: **split-horizon** DNS.
- For on-premises networks, **Route 53 Resolver endpoints** forward queries
  over a VPN or Direct Connect: **inbound** (on-premises asks AWS) and
  **outbound** (AWS asks on-premises).

## Writing records with the API

Records change through a **change batch**, a JSON list of `CREATE`,
`UPSERT` (create or replace) or `DELETE` actions applied all or nothing:

```json
{"Changes": [{"Action": "CREATE", "ResourceRecordSet": {
  "Name": "app.example.com", "Type": "A", "TTL": 60,
  "SetIdentifier": "primary", "Failover": "PRIMARY", "HealthCheckId": "HC_ID",
  "ResourceRecords": [{"Value": "192.0.2.10"}]}}]}
```

`create-hosted-zone` and `create-health-check` need a **caller reference**,
any string unique per request, so a retried request does not create a
second zone; `$(date +%s)` plus a suffix works.

## Your task

Done for you: the foundations VPC (in `VPC_ID`).

1. A public hosted zone **`example.com`**.
2. A health check on **`192.0.2.10`**: **HTTPS**, port **443**, path
   **`/health`**, every **30** seconds, failing after **3** failures.
3. Failover records **`app.example.com`** (type A, TTL **60**): the
   **primary** `192.0.2.10` with that health check, the **secondary**
   `198.51.100.10`.
4. Weighted records **`www.example.com`** (A, TTL 60), with set identifiers
   **`blue`** → `192.0.2.20`, weight **90**, and **`green`** →
   `192.0.2.30`, weight **10**; no other sets.
5. Latency records **`api.example.com`** (A, TTL 60), with set identifiers
   **`us-east-1`** → `192.0.2.40` and **`eu-west-1`** → `198.51.100.40`,
   each with its matching `Region`.
6. A **private** hosted zone **`internal.example.com`** associated with the
   VPC, **`enableDnsHostnames`** turned on in the VPC, and in that zone
   (not the public one) a CNAME **`db.internal.example.com`** →
   `orders.cluster-abc.us-east-1.rds.amazonaws.com`, TTL **300**.

After **Run**:

```
$ ZONE=$(aws route53 list-hosted-zones-by-name --dns-name example.com --query 'HostedZones[0].Id' --output text)
$ aws route53 list-resource-record-sets --hosted-zone-id "$ZONE" \
    --query "ResourceRecordSets[?Type=='A'].[Name,SetIdentifier,ResourceRecords[0].Value]" --output text
api.example.com.	us-east-1	192.0.2.40
api.example.com.	eu-west-1	198.51.100.40
app.example.com.	primary	192.0.2.10
app.example.com.	secondary	198.51.100.10
www.example.com.	blue	192.0.2.20
www.example.com.	green	192.0.2.30
```

Names come back with a trailing dot: `app.example.com.` is the fully
qualified form. The emulator stores the records but answers no real DNS
queries, so `dig` cannot try them here.

## Check yourself

1. The primary of a failover pair has no health check. What happens when
   it goes down?
   *Nothing: Route 53 treats it as healthy and keeps answering with it.*
2. Why can `example.com` itself not be a CNAME to a load balancer, and what
   do you use instead?
   *A CNAME cannot sit next to the apex's NS and SOA records; use an alias
   A record.*
3. Weights 90 and 10 become 3 and 1. What share does `green` get?
   *A quarter: 1 / (3 + 1).*
4. How do you health-check a server in a private subnet?
   *A CloudWatch alarm on a metric, and a health check that follows the
   alarm; the checkers cannot reach private addresses.*
5. Can an instance in another VPC resolve `db.internal.example.com`?
   *Only if that VPC is associated with the private zone.*
