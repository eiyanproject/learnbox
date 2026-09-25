---
title: A hash table
summary: Turning a key into a bucket, handling the collisions that are guaranteed, and why the load factor decides whether it is fast.
order: 2
files: [map.c, map.h]
run: gcc -std=c17 -Wall map.c -o map && ./map
hints:
  - "FNV-1a is five lines: start at 2166136261u, and for each byte XOR it in then multiply by 16777619u. Use unsigned arithmetic throughout."
  - "Each bucket is a linked list of entries - separate chaining. The bucket index is `hash % capacity`."
  - "`map_set` must REPLACE when the key already exists rather than adding a second entry; search the chain first."
  - "Copy the key with strdup-style allocation: the caller's string may not outlive the table, and the table owns what it stores."
---

A hash table turns a key into an array index. Everything hard about it comes
from that not being injective.

## The hash

FNV-1a is short, fast and good enough for a hash table:

```c
unsigned hash = 2166136261u;
for (const unsigned char *p = (const unsigned char *)key; *p; p++) {
    hash ^= *p;
    hash *= 16777619u;
}
```

XOR then multiply, per byte. Use `unsigned` — the multiplication is expected to
wrap, which is defined for unsigned and undefined for signed.

Do not use this for anything security-related: it is not a cryptographic hash,
and an attacker who can choose keys can force every one into the same bucket.

## Collisions are guaranteed

Two keys will map to the same bucket — with 100 buckets and 30 keys it is
overwhelmingly likely. **Separate chaining** keeps a linked list per bucket:

```c
struct Entry { char *key; int value; struct Entry *next; };
struct Map { struct Entry **buckets; size_t capacity; size_t count; };
```

Lookup hashes to a bucket, then walks that short chain comparing keys with
`strcmp`. The hash narrows the search; the comparison confirms it. Skipping the
comparison — trusting the hash alone — is a real bug and gives wrong answers
rarely enough to reach production.

## Load factor

Average chain length is `count / capacity`. Keep it around 0.75 and lookups are
effectively O(1); let it reach 10 and you have a slow linked list with extra
steps. Real implementations grow and rehash when it climbs — this one keeps a
fixed capacity so the chaining stays visible.

## The table owns its keys

```c
entry->key = malloc(strlen(key) + 1);
strcpy(entry->key, key);
```

Storing the caller's pointer means the table breaks when their buffer is reused
or freed. Copy on insert, free on removal — and write that rule down, because
C cannot express it.

## Your turn

In `map.h` and `map.c`:

- `unsigned hash_string(const char *key)` — FNV-1a
- `int map_init(struct Map *m, size_t capacity)`
- `int map_set(struct Map *m, const char *key, int value)` — replaces an
  existing key
- `int map_get(const struct Map *m, const char *key, int *out)` — 1 or 0
- `int map_remove(struct Map *m, const char *key)`
- `size_t map_count(const struct Map *m)`
- `void map_free(struct Map *m)`
