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

A **cache** keeps the answers to expensive questions in memory, so the
database answers them once instead of a thousand times. **ElastiCache**
runs **Valkey**, **Redis OSS** or **Memcached** for you. (Valkey is the open
fork of Redis OSS that AWS now recommends for new caches; the commands and
concepts here are the same. This sandbox uses the `redis` engine.)

## Patterns

- **Lazy loading (cache-aside)**: read the cache; on a miss, read the
  database and put the answer in the cache with a **TTL**. Only what is asked
  for is cached; a miss costs an extra trip; data can be stale until the TTL
  expires.
- **Write-through**: write to the cache whenever the database is written.
  The cache is always fresh, but holds data nobody may read.
- Most real systems combine them, with TTLs as the safety net.

The cache is also the usual home for **session state**, which lets the web
tier stay stateless and scale in without logging users out.

## Surviving an AZ

A Redis/Valkey **replication group** has a primary and up to five read
replicas. With **Multi-AZ** and **automatic failover**, a replica in another
AZ is promoted when the primary's AZ fails. Memcached has no replication -
when a node goes, its data goes.

| | Redis OSS / Valkey | Memcached |
|---|---|---|
| Replication, failover | yes | no |
| Persistence, backups | yes | no |
| Data structures | lists, sets, sorted sets, hashes, streams | strings |
| Multithreaded | per node, limited | yes |

## Encryption

**At rest** (disks and backups) and **in transit** (TLS between clients and
nodes) are both switches at creation - and then clients must connect with
TLS.

## Your task

On top of the foundations VPC, with security group **app** (done for you):

1. a security group **`cache`** allowing **6379 only from `app`**;
2. a cache subnet group **`cache`** of the two private subnets;
3. a replication group **`sessions`**: engine **redis**, **cache.t3.micro**,
   **two** nodes, **automatic failover** and **Multi-AZ** on, **encrypted at
   rest and in transit**, in the `cache` subnet group with the `cache`
   security group.
