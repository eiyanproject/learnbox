#ifndef MAP_H
#define MAP_H

#include <stddef.h>

struct Entry {
    char *key; /* owned by the table */
    int value;
    struct Entry *next;
};

struct Map {
    struct Entry **buckets;
    size_t capacity;
    size_t count;
};

unsigned hash_string(const char *key);
int map_init(struct Map *m, size_t capacity);
int map_set(struct Map *m, const char *key, int value);
int map_get(const struct Map *m, const char *key, int *out);
int map_remove(struct Map *m, const char *key);
size_t map_count(const struct Map *m);
void map_free(struct Map *m);

#endif
