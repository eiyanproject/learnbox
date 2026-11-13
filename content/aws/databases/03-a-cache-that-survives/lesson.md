---
title: A cache that survives an AZ
summary: ElastiCache for Redis OSS with a replica in another AZ, automatic failover, encryption at rest and in transit - and the caching patterns that decide what it holds.
order: 3
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`aws elasticache create-cache-subnet-group --cache-subnet-group-name cache --cache-subnet-group-description cache --subnet-ids \"$PRIVATE_A\" \"$PRIVATE_B\"`."
  - "`aws elasticache create-replication-group --replication-group-id sessions --replication-group-description \"user sessions\" --engine redis --cache-node-type cache.t3.micro --num-cache-clusters 2 --automatic-failover-enabled --multi-az-enabled --at-rest-encryption-enabled --transit-encryption-enabled --cache-subnet-group-name cache --security-group-ids \"$CACHE_SG\"`."
  - "Redis listens on 6379. The cache's security group allows 6379 from the app's group only."
---

The product page of a shop asks the database the same questions thousands
of times a minute: this product's price, its reviews, the categories menu.
Each answer is identical for everyone, and each one costs the database work.
A **cache** keeps those answers in **memory**, so the database answers each
question once instead of a thousand times, and the app gets the answer in
well under a millisecond.

**ElastiCache** runs three in-memory engines for you: **Valkey**, **Redis
OSS** and **Memcached**. Valkey is the open-source continuation of Redis
OSS, which AWS now recommends for new caches; the commands and concepts are
the same. This sandbox uses the `redis` engine.

This lesson builds a cache for **user sessions** that keeps working when an
Availability Zone fails.

## Caching patterns

What goes into the cache, and when, is a choice with consequences. The two
classic patterns:

- **Lazy loading** (also called **cache-aside**): the app asks the cache
  first. On a **hit**, it uses the answer. On a **miss**, it asks the
  database, then puts the answer in the cache with a **TTL** (an expiry
  time), so the next request hits.

  ```text
  value = cache.get(key)
  if value is missing:
      value = database.query(...)
      cache.set(key, value, ttl=300)      # expires after 5 minutes
  return value
  ```

  Only data someone actually asks for is cached, and a cache failure only
  slows things down. The cost: every miss is an extra trip, and an answer
  can be **stale** (out of date) until its TTL expires.

- **Write-through**: whenever the app writes to the database, it writes the
  new value to the cache too. The cache is always fresh, but fills with data
  nobody may ever read, and every write is two writes.

Most real systems combine them, with TTLs as the safety net that eventually
fixes anything stale.

The cache is also the usual home for **session state** (who is logged in,
what is in their basket). With sessions in a shared cache instead of on each
web server, any server can serve any request, so the Auto Scaling group from
the last section can add and remove servers without logging anyone out.

## Surviving an AZ

A Redis OSS or Valkey **replication group** is one **primary** node, which
takes the writes, and up to five **replicas**, which copy it continuously
and can serve reads. Turn on **Multi-AZ** and **automatic failover**, with
nodes spread across AZs, and when the primary's node or AZ fails, a replica
in another AZ is **promoted** to primary, usually within a minute or so.
The group's **primary endpoint**, the DNS name the app connects to, moves to
the new primary, so the app reconnects without a configuration change.

```text
 app ──> primary endpoint (master.sessions...cache.amazonaws.com)
            │
            ├── primary  in private-a   (takes writes)
            └── replica  in private-b   (copies the primary; promoted if private-a's AZ fails)
```

Replication is **asynchronous**: the primary confirms a write before the
replicas have it, so a failover can lose the last moments of writes. Fine
for a cache or sessions, not for data that exists nowhere else. And a
reboot you start yourself does not fail over; the primary is simply away
while it restarts.

Failover needs at least two nodes: with one there is nothing to promote.
(Real ElastiCache refuses automatic failover on a one-node group; the
emulator is more lenient, so count your nodes.)

Memcached has no replication: when a node goes, its data goes. That, and
the other differences, are a common exam comparison:

| | Redis OSS / Valkey | Memcached |
|---|---|---|
| Replication and automatic failover | yes | no |
| Persistence, backups and restore | yes | no |
| Data types | strings, lists, sets, sorted sets, hashes, streams | strings only |
| Multithreaded | limited, per node | yes, uses many cores per node |
| Choose it for | sessions, leaderboards, queues, anything that must survive a failure | the simplest possible cache, where losing it only costs a cold start |

## Encryption

**At rest** (the nodes' disks and backups) and **in transit** (TLS
between the app and the nodes) are both switches you choose **at
creation**; turning at-rest encryption on later means restoring a backup
into a new replication group. With encryption in transit on, clients **must** connect using
TLS; a client configured for plain connections fails to connect at all,
which is the usual first surprise after turning it on.

Adding a cache is not a switch: the **application** decides what to read
from it and write to it, so lazy loading or write-through means code
changes. (DAX, for DynamoDB only, is the exception.)

## Your task

On top of the Foundations VPC, with a security group **app** for the
application (done for you, in `APP_SG`):

1. a security group **`cache`** whose only inbound rule is TCP **6379**
   (Redis's port) **from the `app` group**, with no address ranges;
2. a cache subnet group **`cache`** made of the two **private** subnets
   (like RDS's DB subnet group: the subnets the nodes may be placed in);
3. a replication group **`sessions`** with:
   - engine **redis**, node type **cache.t3.micro**;
   - **two** nodes (`--num-cache-clusters 2`: a primary and one replica);
   - **automatic failover** and **Multi-AZ** on;
   - encryption **at rest and in transit**;
   - the `cache` subnet group and the `cache` security group.

After **Run**:

```
$ aws elasticache describe-replication-groups --replication-group-id sessions \
    --query 'ReplicationGroups[0].[Status,AutomaticFailover,MultiAZ,NodeGroups[0].PrimaryEndpoint.Address]'
[
    "available",
    "enabled",
    "enabled",
    "master.sessions.a3q4wu.use1.cache.amazonaws.com"
]
```

💸 Each node is billed by the hour, so a two-node group costs twice one
node: the price of surviving an AZ.

## Check yourself

1. Lazy loading: what happens on a cache miss?
   *The app reads the database, then stores the answer in the cache with a
   TTL.*
2. Why keep sessions in a cache rather than on each web server?
   *Any server can serve any user, so servers can be added and removed
   without logging anyone out.*
3. Memcached or Redis OSS/Valkey for data that must survive a node failure?
   *Redis OSS or Valkey, with a replica and automatic failover.*
4. Why can a failover lose the very latest writes?
   *Replication to the replica is asynchronous.*
