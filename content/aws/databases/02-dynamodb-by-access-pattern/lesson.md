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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **SQL** | the query language of relational databases |
| **DynamoDB** | a serverless key-value and document database |
| **serverless** | no servers for you to choose or patch |
| **on-demand** / **provisioned** | pay per request / pay for capacity you reserve |
| **join** | combining tables in a query; DynamoDB has none |
| **ad-hoc query** | a question nobody planned for |
| **access pattern** | an exact question the app will ask; design the table around them |
| **table** | a collection of items |
| **item** | like a row; at most 400 KB |
| **attribute** | like a column; only key attributes are fixed |
| **typed value** | `{"S": "..."}` string, `{"N": "42.50"}` number (sent as a string), `B` binary |
| **partition key** | decides where an item lives; choose one with many distinct values |
| **hash** | turn a value into a number that picks a storage partition |
| **partition** | one piece of the table's storage |
| **sort key** | orders items within one partition key |
| **primary key** | partition key plus sort key; unique per item |
| **`HASH`** / **`RANGE`** | the API's names for partition key / sort key |
| **global secondary index (GSI)** | a second set of keys over the same items; eventually consistent |
| **eventually consistent** | a new write may take a moment to appear |
| **strongly consistent** | a read always shows the latest write |
| **projection** | which attributes are copied into an index; `ALL` copies every one |
| **local secondary index (LSI)** | same partition key, different sort key; only at table creation |
| **`Query`** | reads items by key, quickly |
| **`Scan`** | reads the whole table; never on a request path |
| **`ACTIVE`** | the table is ready to use |
| **TTL** | an attribute holding an expiry time; DynamoDB deletes expired items, eventually |
| **epoch seconds** | seconds since 1 January 1970, UTC |
| **point-in-time recovery (PITR)** | continuous backups: restore to any second in the last 35 days |
| **Streams** | a record of every change for 24 hours, for Lambda to react to |
| **global tables** | a table replicated to several Regions, writable in all |
| **key condition expression** | the `Query`'s key test, such as `pk = :c` |
| **value placeholder** | `:c`, filled in from `--expression-attribute-values` |
| **name placeholder** | `#s`, filled in from `--expression-attribute-names` |
| **reserved word** | a name like `status` that must go through a name placeholder |
| **RCU** / **WCU** | read and write capacity units: one 4 KB strong read / one 1 KB write per second |
| **DAX** | an in-memory cache in front of DynamoDB with the same API |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws dynamodb create-table --table-name T --attribute-definitions ... --key-schema ... --billing-mode PAY_PER_REQUEST` | creates a table |
| `--global-secondary-indexes file://...` | adds GSIs at creation |
| `aws dynamodb wait table-exists --table-name T` | waits until it is `ACTIVE` |
| `aws dynamodb update-time-to-live --table-name T --time-to-live-specification Enabled=true,AttributeName=expires_at` | turns on TTL |
| `aws dynamodb update-continuous-backups --table-name T --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true` | turns on PITR |
| `aws dynamodb batch-write-item --request-items file://items.json` | writes up to 25 items |
| `aws dynamodb query --table-name T --key-condition-expression 'pk = :c' --expression-attribute-values '{...}'` | a query |
| `--index-name by-status` | queries an index instead |
| `--no-scan-index-forward` | reads the sort key backwards: newest first |

### Errors

| Error | Means |
|---|---|
| `ValidationException ... Number of attributes in KeySchema does not exactly match number of attributes defined in AttributeDefinitions` | declared an attribute no key uses |
| `ValidationException ... Attribute name is a reserved keyword; reserved keyword: status` | `status` used without a `#` name placeholder (real DynamoDB) |

---

A relational database like last lesson's lets you ask almost any question
with SQL, at the cost of servers to size and a ceiling on how far one
database can grow. **DynamoDB** makes the opposite trade. It is a
**serverless** key-value and document database: there are no instances to
choose or patch, reads and writes take single-digit milliseconds whether
the table holds a thousand items or a billion, and you pay per request
(**on-demand**) or for capacity you reserve (**provisioned**).

The catch: DynamoDB answers only the questions its **keys** were designed
for, quickly, and nothing else efficiently. There are no joins and no
ad-hoc queries. So you design the table around your **access patterns**,
the exact questions the app will ask, **before** writing code. This lesson's
app asks two:

1. "Show customer 1's orders, newest first."
2. "Show all orders with status SHIPPED, by date."

## Items and attributes

A table holds **items** (like rows), each a set of **attributes** (like
columns). Only the key attributes are fixed by the table; every other
attribute can vary from item to item, and needs no declaring. In the API,
every value is written with its **type**: `{"S": "CUSTOMER#1"}` is a string,
`{"N": "42.50"}` a number (sent as a string, so no precision is lost),
plus booleans, lists, maps and sets.

## Keys

- The **partition key** (here `pk`) decides **where** an item lives:
  DynamoDB hashes it to pick a storage partition. Requests are spread across
  partitions, so choose a key with many distinct values; a key like
  `status`, with three values, would send all the traffic to three places.
- The optional **sort key** (here `sk`) orders the items **within** one
  partition key, so one `Query` can read a range of them: "all of customer
  1's items whose sort key starts with `ORDER#`, newest first".

Together they are the item's **primary key**, which must be unique. A common
design puts several kinds of item in one table, distinguished by prefixes:

```text
 pk            sk                       status    total
 CUSTOMER#1    ORDER#2026-11-01#0001    SHIPPED   42.50
 CUSTOMER#1    ORDER#2026-11-05#0002    SHIPPED   18.00
 CUSTOMER#1    ORDER#2026-11-09#0003    PLACED    99.95
 CUSTOMER#2    ORDER#2026-11-08#0004    PLACED     7.25
```

Putting the date in the sort key makes "newest first" a matter of reading
the partition backwards. The `#` is only a separator people use by
convention.

## Indexes

Access pattern 2 asks by `status`, which is not the table's partition key,
so the table cannot answer it efficiently. A **global secondary index**
(GSI) is a second set of keys over the same items: here, `status` as the
partition key and `sk` as the sort key, so "SHIPPED, by date" becomes one
`Query` on the index. DynamoDB keeps the index up to date as items change, a little behind
the table: reads from a GSI are **eventually consistent**, so an item just
written may take a moment to appear in it. An item without the index's key
attribute (no `status`) is simply not in the index.
**Projection** `ALL` copies every attribute into the index, so a query on it
returns whole items.

A **local secondary index** (LSI) keeps the table's partition key with a
different sort key, and can only be created together with the table.

`Scan` reads the **whole** table and filters afterwards. It is fine for a
test of four items, and never for a request path: on a big table it is slow,
and you pay for every item read.

### Declaring the key attributes

`--attribute-definitions` lists the attributes used as keys, by the table
**or** by any index, with their types (`S`, `N` or `B` for binary), and only
those. Declaring an attribute no key uses is an error:

```
An error occurred (ValidationException) when calling the CreateTable operation: One or more parameter values were invalid: Number of attributes in KeySchema does not exactly match number of attributes defined in AttributeDefinitions
```

So `orders` declares three: `pk`, `sk` and `status` (for the index). In
`--key-schema`, `HASH` means partition key and `RANGE` sort key, names left
over from DynamoDB's early days.

A new table takes a few seconds to become `ACTIVE`, and settings like TTL
cannot be changed until then. `aws dynamodb wait table-exists --table-name
orders` pauses the script until it is ready.

## Housekeeping features

- **TTL** (time to live): name an attribute that holds an expiry time, as
  a **Number** in epoch seconds (seconds since 1 January 1970, UTC); items
  whose attribute is missing or not a Number are never expired. DynamoDB
  deletes items some time after that moment passes, usually within a few
  days, free of charge. Until then an expired item can still be read, so
  queries should filter it out. Ideal for sessions and temporary data.
- **Point-in-time recovery** (PITR): continuous backups, so the table can be
  restored to any second in the last 35 days, after a bad deploy or an
  accidental mass delete.
- **Streams** record every change to the table, for Lambda functions to
  react to; **global tables** build on them to replicate a table across
  Regions.

## Writing and reading items

`batch-write-item` writes up to 25 items in one call, from a file that maps
the table name to a list of requests:

```json
{
  "orders": [
    { "PutRequest": { "Item": {
      "pk": { "S": "CUSTOMER#1" }, "sk": { "S": "ORDER#2026-11-01#0001" },
      "status": { "S": "SHIPPED" }, "total": { "N": "42.50" } } } }
  ]
}
```

A `Query` names the partition key value in a **key condition expression**,
with placeholders for the values (`:c`), so values never have to be pasted
into the expression text:

```
$ aws dynamodb query --table-name orders \
    --key-condition-expression 'pk = :c' \
    --expression-attribute-values '{":c":{"S":"CUSTOMER#1"}}' --no-scan-index-forward \
    --query 'Items[].[sk.S,status.S,total.N]' --output table
-----------------------------------------------
|                    Query                    |
+------------------------+----------+---------+
|  ORDER#2026-11-09#0003 |  PLACED  |  99.95  |
|  ORDER#2026-11-05#0002 |  SHIPPED |  18.00  |
|  ORDER#2026-11-01#0001 |  SHIPPED |  42.50  |
+------------------------+----------+---------+
```

`--no-scan-index-forward` reads the sort key backwards: newest first, which
is access pattern 1.

## More DynamoDB facts

- An item can be at most **400 KB**.
- **Capacity modes**: **on-demand** (pay per request, scales instantly; the
  usual default now) or **provisioned**, where you set **read and write
  capacity units** (one RCU is one strongly consistent read per second of up
  to 4 KB; one WCU one write per second of up to 1 KB), optionally with auto
  scaling. Provisioned is cheaper for steady, predictable load.
- **DAX** is an in-memory cache in front of DynamoDB with microsecond reads
  and the same API, so code barely changes.
- **Streams** record each change for 24 hours, for Lambda triggers;
  **global tables** replicate a table to several Regions, writable in all.
- Any restore, from point-in-time recovery or a backup, creates a **new**
  table.

## Your task

1. A table **`orders`**: partition key **`pk`** (string), sort key **`sk`**
   (string), **on-demand** (`--billing-mode PAY_PER_REQUEST`), with a GSI
   **`by-status`** keyed on **`status`** (string), with **`sk`** as its sort
   key, projecting **all** attributes.
2. **TTL** on the attribute **`expires_at`**, and **point-in-time
   recovery** on. (Wait for the table first.)
3. Fill in **`items.json`** (the starter has the empty list) and write it
   with `batch-write-item`: **three** orders for `CUSTOMER#1` and **one**
   for `CUSTOMER#2`, each with:
   - an `sk` starting `ORDER#`, such as `ORDER#2026-11-01#0001`;
   - a `status`, `PLACED` or `SHIPPED`; use **both** across the four
     orders, since the check queries the index for each;
   - a `total`, typed as a **number** (`"N"`).

After **Run**, try both access patterns: the query above, and the index:

```
aws dynamodb query --table-name orders --index-name by-status \
  --key-condition-expression '#s = :s' --expression-attribute-names '{"#s":"status"}' \
  --expression-attribute-values '{":s":{"S":"SHIPPED"}}'
```

`status` is one of DynamoDB's **reserved words**, so an expression must
refer to it through a name placeholder, `#s`, defined in
`--expression-attribute-names`. Real DynamoDB rejects `status = :s` with
`ValidationException ... Attribute name is a reserved keyword; reserved
keyword: status`; the emulator lets it pass, so use the placeholder anyway.

## Check yourself

1. Why design the keys before writing code?
   *DynamoDB only answers the questions its keys and indexes were built
   for, efficiently.*
2. You need all orders with status SHIPPED. Query the table, or the index?
   *The `by-status` GSI: `status` is not the table's partition key.*
3. Why avoid `Scan` in a request path?
   *It reads the whole table, slowly and at the cost of every item read.*
4. Why does the query use `#s` for `status`?
   *`status` is a reserved word in DynamoDB expressions.*
5. An item's `expires_at` passed an hour ago. Can it still be read?
   *Yes, until TTL deletes it, which can take days; filter it out.*
