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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **hash table** | turns a key into an array index for fast lookup |
| **hash function** | turns a key into a number |
| **injective** | different inputs always give different outputs; hashes are not |
| **FNV-1a** | a short, fast, non-cryptographic hash: XOR each byte, then multiply |
| **test values** | published inputs and outputs to check an implementation |
| **cryptographic hash** | one designed to resist attackers; FNV-1a is not |
| **bucket** | one slot of the table's array |
| **collision** | two keys landing in the same bucket |
| **separate chaining** | a linked list per bucket |
| **chain** | the list of entries in one bucket |
| **load factor** | `count / capacity`: average chain length; keep it near 0.75 |
| **rehash** | grow the table and move every entry |
| **owns its keys** | the table copies keys on insert and frees them on removal |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=c17 -Wall map.c -o map && ./map` | builds and runs |

### C names

| Name | What it does |
|---|---|
| `hash ^= *p; hash *= 16777619u;` | one FNV-1a step |
| `2166136261u` | FNV-1a's starting value |
| `hash % capacity` | picks the bucket |
| `struct Entry **buckets` | an array of chain heads |
| `strcmp(a, b)` | 0 when two strings are equal; confirms a match |
| `malloc(strlen(key) + 1); strcpy(...)` | copies a key, terminator included |
| `%08x` | `printf` hexadecimal, 8 digits with leading zeros |

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
wrap, which is defined for unsigned and undefined for signed. FNV-1a publishes
test values, so you can check an implementation against them:

```c
#include <stdio.h>

unsigned fnv1a(const char *key) {
    unsigned hash = 2166136261u;
    for (const unsigned char *p = (const unsigned char *)key; *p; p++) {
        hash ^= *p;
        hash *= 16777619u;
    }
    return hash;
}

int main(void) {
    printf("%08x %08x %08x\n", fnv1a(""), fnv1a("a"), fnv1a("foobar"));
    printf("bucket of \"foobar\" in 100: %u\n", fnv1a("foobar") % 100);
    return 0;
}
```

```output
811c9dc5 e40c292c bf9cf968
bucket of "foobar" in 100: 20
```

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
