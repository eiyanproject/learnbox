---
title: A linked list, and the pointer-to-pointer trick
summary: Nodes joined by pointers, why removal is where everyone writes a bug, and the idiom that removes the special case.
order: 3
files: [list.c, list.h]
run: gcc -std=c17 -Wall list.c -o list && ./list
hints:
  - "`list_push_front` allocates a node, points its next at the current head, and sets the head to it. Return 1 on success, 0 if malloc failed."
  - "`list_remove` is the interesting one: walk with `struct Node **link = &list->head`, and when you find the value do `*link = (*link)->next` then free."
  - "The pointer-to-pointer removes the special case for the head: `*link` IS the head pointer on the first iteration, and a node's next pointer afterwards."
  - "`list_free` must walk saving `next` BEFORE freeing the node - reading node->next after free is a use-after-free."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **linked list** | nodes joined by pointers |
| **node** | one element: a value and a pointer to the next node |
| **head** | the first node |
| **contiguous** | side by side in memory, like an array |
| **cache** | fast memory near the CPU; it favours contiguous data |
| **data structure** | a way of organising data in memory |
| **special case** | extra code for one situation, such as removing the head |
| **pointer to pointer** | `struct Node **link`: points at the pointer that points to a node |
| **idiom** | a standard way experienced programmers write something |
| **use-after-free** | reading `node->next` after `free(node)` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `gcc -std=c17 -Wall list.c -o list && ./list` | builds and runs |

### C names

| Name | What it does |
|---|---|
| `struct Node { int value; struct Node *next; };` | a node |
| `cur->next` | the next node |
| `&list->head` | the address of the head pointer |
| `link = &(*link)->next;` | move `link` to the next node's `next` field |
| `*link = dead->next;` | unlink a node, whichever pointer pointed at it |
| `struct Node *next = node->next; free(node);` | save the next pointer before freeing |

---

A linked list is nodes joined by pointers. Each node owns its value and a
pointer to the next:

```c
struct Node {
    int value;
    struct Node *next;
};
```

It is a poor default data structure — an array is faster for almost everything
because it is contiguous and the cache likes that. It is worth learning anyway,
because the pointer discipline it demands is the same discipline every other C
data structure needs.

## Removal is where the bugs are

The obvious version needs a special case for the head, and a `prev` pointer:

```c
struct Node *prev = NULL, *cur = head;
while (cur && cur->value != target) { prev = cur; cur = cur->next; }
if (!cur) return 0;
if (prev) prev->next = cur->next; else head = cur->next;   /* two cases */
free(cur);
```

That `if (prev) ... else ...` is where the bug lives, because the head case is
rarely the one you test.

## The pointer-to-pointer idiom

```c
struct Node **link = &list->head;
while (*link && (*link)->value != target) {
    link = &(*link)->next;
}
if (!*link) return 0;
struct Node *dead = *link;
*link = dead->next;
free(dead);
```

`link` points at **the pointer that points to the current node** — the head
pointer on the first iteration, and some node's `next` field afterwards.
Writing through it updates the right one without knowing which it was. The
special case is gone because there was never really two cases, only two places
the same pointer could live.

This is one of the genuinely elegant things in C, and worth the ten minutes it
takes to see.

## Freeing

```c
while (node) {
    struct Node *next = node->next;   /* save it first */
    free(node);
    node = next;
}
```

Reading `node->next` after `free(node)` is a use-after-free. It usually appears
to work, which is what makes it dangerous.

## Your turn

In `list.h` and `list.c`, with `struct Node` and
`struct List { struct Node *head; int count; }`:

- `void list_init(struct List *list)`
- `int list_push_front(struct List *list, int value)` — 1 or 0
- `int list_push_back(struct List *list, int value)`
- `int list_contains(const struct List *list, int value)`
- `int list_remove(struct List *list, int value)` — 1 if removed, using the
  pointer-to-pointer idiom
- `void list_free(struct List *list)`
