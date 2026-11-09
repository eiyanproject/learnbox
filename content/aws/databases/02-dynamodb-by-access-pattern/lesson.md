---
title: DynamoDB, designed by access pattern
summary: A table shaped around the questions the app asks - partition and sort keys, a global secondary index, on-demand capacity, TTL for expiry and point-in-time recovery - and items written and queried from the CLI.
order: 2
files: [setup.sh, items.json]
run: awslab run setup.sh
hints:
  - "Keys and the index: `--attribute-definitions AttributeName=pk,AttributeType=S AttributeName=sk,AttributeType=S AttributeName=status,AttributeType=S --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE --global-secondary-indexes 'IndexName=by-status,KeySchema=[{AttributeName=status,KeyType=HASH},{AttributeName=sk,KeyType=RANGE}],Projection={ProjectionType=ALL}' --billing-mode PAY_PER_REQUEST`."
  - "Only key attributes (of the table or an index) go in --attribute-definitions. Everything else in an item needs no declaring."
  - "`aws dynamodb update-time-to-live --table-name orders --time-to-live-specification Enabled=true,AttributeName=expires_at` and `aws dynamodb update-continuous-backups --table-name orders --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true`."
  - "`aws dynamodb batch-write-item --request-items file://items.json` writes up to 25 items; items.json maps the table name to a list of `{\"PutRequest\": {\"Item\": {...}}}`, each attribute typed: `{\"pk\": {\"S\": \"CUSTOMER#1\"}}`."
---

**DynamoDB** is a serverless key-value and document database: no instances,
single-digit-millisecond reads and writes at any scale, and you pay per
request (on-demand) or per provisioned capacity. The catch is that you design
the table around your **access patterns** - the questions the app will ask -
before you write a line of code. There are no joins and no ad-hoc queries.

## Keys

- The **partition key** (`pk`) decides where an item lives. Requests spread
  across partitions, so pick a key with many distinct values.
- The optional **sort key** (`sk`) orders items within a partition, so one
  `Query` reads a range: "all of customer 1's orders, newest first".
- A common pattern puts several kinds of item in one table with prefixes:
  `pk = CUSTOMER#1`, `sk = ORDER#2026-11-09#0007`.

## Indexes

A **global secondary index** (GSI) is a second set of keys over the same
items - a different question answered efficiently. "All orders with status
SHIPPED, by date" needs `status` as a partition key, so it gets an index. A
**local secondary index** shares the table's partition key with a different
sort key, and can only be created with the table.

`Scan` reads the whole table - fine for a test, never for a request path.

## Housekeeping features

- **TTL**: name an attribute holding an epoch time; DynamoDB deletes items
  after it passes, free of charge (usually within a few days).
- **Point-in-time recovery**: restore the table to any second in the last
  35 days.
- **Streams**: a change log for Lambda triggers and replication; **global
  tables** build on it for multi-Region.

## Your task

1. A table **`orders`**: partition key **`pk`** (string), sort key **`sk`**
   (string), **on-demand**, with a GSI **`by-status`** keyed on **`status`**
   with **`sk`** as its sort key, projecting all attributes.
2. **TTL** on the attribute **`expires_at`**, and **point-in-time
   recovery** on.
3. Fill in **`items.json`** and write it with `batch-write-item`: **three**
   orders for `CUSTOMER#1` and **one** for `CUSTOMER#2`, each with
   `sk` like `ORDER#2026-11-0X#000N`, a `status` (`PLACED` or `SHIPPED` -
   use both) and a `total` (a number).

After **Run**, try the access patterns:

```
aws dynamodb query --table-name orders \
  --key-condition-expression 'pk = :c' \
  --expression-attribute-values '{":c":{"S":"CUSTOMER#1"}}' --no-scan-index-forward
aws dynamodb query --table-name orders --index-name by-status \
  --key-condition-expression '#s = :s' --expression-attribute-names '{"#s":"status"}' \
  --expression-attribute-values '{":s":{"S":"SHIPPED"}}'
```

(`status` is a reserved word in DynamoDB expressions, hence `#s`.)
