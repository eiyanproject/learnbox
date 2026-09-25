#ifndef VEC_H
#define VEC_H

#include <stddef.h>

struct Vec {
    void *data;
    size_t elem_size;
    size_t count;
    size_t capacity;
};

int vec_init(struct Vec *v, size_t elem_size);
int vec_push(struct Vec *v, const void *elem);
void *vec_get(const struct Vec *v, size_t index);
int vec_pop(struct Vec *v, void *out);
size_t vec_count(const struct Vec *v);
void vec_free(struct Vec *v);

#endif
