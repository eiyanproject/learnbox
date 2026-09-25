#include "map.h"

#include <stdlib.h>
#include <string.h>

unsigned hash_string(const char *key) {
    /* FNV-1a. Unsigned because the multiply is meant to wrap, which is
       defined for unsigned and undefined for signed. */
    unsigned hash = 2166136261u;
    for (const unsigned char *p = (const unsigned char *)key; *p != '\0'; p++) {
        hash ^= *p;
        hash *= 16777619u;
    }
    return hash;
}

int map_init(struct Map *m, size_t capacity) {
    if (capacity == 0) {
        return 0;
    }
    m->buckets = calloc(capacity, sizeof *m->buckets);
    if (m->buckets == NULL) {
        return 0;
    }
    m->capacity = capacity;
    m->count = 0;
    return 1;
}

static struct Entry **find_link(const struct Map *m, const char *key) {
    size_t index = hash_string(key) % m->capacity;
    struct Entry **link = &m->buckets[index];
    while (*link != NULL && strcmp((*link)->key, key) != 0) {
        link = &(*link)->next;
    }
    return link;
}

int map_set(struct Map *m, const char *key, int value) {
    struct Entry **link = find_link(m, key);
    if (*link != NULL) {
        (*link)->value = value; /* replace, do not add a second entry */
        return 1;
    }
    struct Entry *entry = malloc(sizeof *entry);
    if (entry == NULL) {
        return 0;
    }
    /* The table owns its keys: the caller's buffer may not outlive us. */
    size_t n = strlen(key) + 1;
    entry->key = malloc(n);
    if (entry->key == NULL) {
        free(entry);
        return 0;
    }
    memcpy(entry->key, key, n);
    entry->value = value;
    entry->next = NULL;
    *link = entry;
    m->count++;
    return 1;
}

int map_get(const struct Map *m, const char *key, int *out) {
    struct Entry **link = find_link(m, key);
    if (*link == NULL) {
        return 0;
    }
    if (out != NULL) {
        *out = (*link)->value;
    }
    return 1;
}

int map_remove(struct Map *m, const char *key) {
    struct Entry **link = find_link(m, key);
    if (*link == NULL) {
        return 0;
    }
    struct Entry *dead = *link;
    *link = dead->next;
    free(dead->key);
    free(dead);
    m->count--;
    return 1;
}

size_t map_count(const struct Map *m) {
    return m->count;
}

void map_free(struct Map *m) {
    for (size_t i = 0; i < m->capacity; i++) {
        struct Entry *entry = m->buckets[i];
        while (entry != NULL) {
            struct Entry *next = entry->next;
            free(entry->key);
            free(entry);
            entry = next;
        }
    }
    free(m->buckets);
    m->buckets = NULL;
    m->capacity = 0;
    m->count = 0;
}
