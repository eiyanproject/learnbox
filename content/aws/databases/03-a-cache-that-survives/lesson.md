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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **cache** | keeps answers in memory so the database answers each question once |
| **in-memory** | held in RAM: sub-millisecond reads |
| **ElastiCache** | runs Valkey, Redis OSS or Memcached for you |
| **Valkey** / **Redis OSS** | the same kind of in-memory store; Valkey is the open-source continuation AWS recommends |
| **Memcached** | the simplest cache: strings only, no replication |
| **lazy loading (cache-aside)** | ask the cache; on a miss, ask the database and store the answer with a TTL |
| **hit** / **miss** | the answer is in the cache / is not |
| **TTL** | how long a cached answer lives before it expires |
| **stale** | out of date |
| **write-through** | every database write also writes the cache |
| **session state** | who is logged in and what is in their basket |
| **replication group** | one primary node plus up to five replicas |
| **node** | one cache server |
| **primary** / **replica** | takes writes / copies it and can serve reads |
| **Multi-AZ** with **automatic failover** | a replica in another AZ is promoted when the primary fails |
| **promote** | make a replica the new primary |
| **primary endpoint** | the DNS name the app connects to; it follows the primary |
| **asynchronous replication** | a failover can lose the last moments of writes |
| **persistence** | keeping data on disk, so it survives a restart; Redis has it, Memcached not |
| **sorted set**, **hash**, **stream** | Redis data types |
| **multithreaded** | uses several CPU cores at once |
| **encryption at rest** / **in transit** | on disks and backups / TLS to the client; both chosen at creation |
| **cache subnet group** | the subnets the nodes may be placed in |
| **node type** | the node's size, such as `cache.t3.micro` |
| **port 6379** | Redis's port |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws elasticache create-cache-subnet-group --cache-subnet-group-name N --cache-subnet-group-description D --subnet-ids A B` | creates a cache subnet group |
| `aws elasticache create-replication-group --replication-group-id N --replication-group-description D --engine redis --cache-node-type cache.t3.micro --num-cache-clusters 2` | creates a primary and one replica |
| `--automatic-failover-enabled --multi-az-enabled` | failover across AZs |
| `--at-rest-encryption-enabled --transit-encryption-enabled` | encryption on disk and on the wire |
| `--cache-subnet-group-name N --security-group-ids G` | placement and firewall |
| `aws elasticache describe-replication-groups --replication-group-id N` | shows status and the primary endpoint |

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
