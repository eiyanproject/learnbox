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

**Route 53** is AWS's DNS: authoritative hosted zones, health checks, and
**routing policies** that decide which answer each query gets.

## Routing policies

| Policy | Answers with | Use it for |
|---|---|---|
| Simple | the one record set | a single resource |
| **Failover** | the primary while its health check passes, else the secondary | active/passive DR |
| **Weighted** | records in proportion to their weights | canaries, blue/green, A/B |
| **Latency** | the Region with the lowest latency to the resolver | multi-Region active/active |
| Geolocation | by the user's continent, country or state | compliance, localized content |
| Geoproximity | by distance, with a bias | shifting traffic between Regions |
| Multivalue | up to eight healthy records | simple client-side spreading |
| IP-based | by the client's IP range | routing known networks |

Every non-simple record set needs a **`SetIdentifier`** that is unique among
records with the same name and type.

## Health checks

A health check probes an endpoint (HTTP, HTTPS or TCP) from many locations,
every 30 seconds (or 10, at extra cost), and fails after N consecutive
failures. Failover records follow it; any record can be marked
`EvaluateTargetHealth` when it is an **alias** to an AWS resource such as a
load balancer. For a private endpoint, alarm on a CloudWatch metric
instead - Route 53 checkers live on the internet.

## Alias records and TTLs

An **alias** record points at an AWS resource (ALB, CloudFront, S3 website,
another record) - free of charge, allowed at the zone apex, and it follows
the resource's IPs. Lower TTLs (60 s) make failover and weight changes take
effect sooner, at the cost of more queries.

## Private hosted zones

A **private** zone answers only queries from the VPCs associated with it,
through the VPC's resolver (`.2` address). The VPC needs `enableDnsSupport`
and `enableDnsHostnames`. Names in a private zone can shadow public ones
for those VPCs - a split-horizon setup.

## Your task

Done for you: the foundations VPC.

1. A public hosted zone **`example.com`**.
2. A health check on **`192.0.2.10`**: HTTPS, port 443, path **`/health`**,
   every **30** s, failing after **3** failures.
3. Failover records **`app.example.com`** (A, TTL **60**): **primary**
   `192.0.2.10` with that health check, **secondary** `198.51.100.10`.
4. Weighted records **`www.example.com`** (A, TTL 60): `blue` →
   `192.0.2.20` weight **90**, `green` → `192.0.2.30` weight **10**.
5. Latency records **`api.example.com`** (A, TTL 60): `us-east-1` →
   `192.0.2.40`, `eu-west-1` → `198.51.100.40`.
6. A private hosted zone **`internal.example.com`** for the VPC, with
   `enableDnsHostnames` on in the VPC, and a CNAME
   **`db.internal.example.com`** → `orders.cluster-abc.us-east-1.rds.amazonaws.com`
   (TTL 300).

After **Run**: `aws route53 list-resource-record-sets --hosted-zone-id
"$(aws route53 list-hosted-zones-by-name --dns-name example.com --query
'HostedZones[0].Id' --output text)"`.
