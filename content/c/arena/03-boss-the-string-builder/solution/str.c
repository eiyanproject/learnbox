#include "str.h"

#include <stdlib.h>
#include <string.h>

/* Make room for a string of `need` characters plus its terminator. */
static int reserve(Str *s, size_t need) {
    if (need + 1 <= s->cap) {
        return 0;
    }
    size_t cap = s->cap * 2;
    if (cap < need + 1) {
        cap = need + 1;
    }
    char *grown = realloc(s->data, cap);
    if (grown == NULL) {
        return -1;
    }
    s->data = grown;
    s->cap = cap;
    return 0;
}

int str_init(Str *s) {
    s->data = malloc(16);
    if (s->data == NULL) {
        s->len = 0;
        s->cap = 0;
        return -1;
    }
    s->data[0] = '\0';
    s->len = 0;
    s->cap = 16;
    return 0;
}

int str_insert(Str *s, size_t at, const char *text) {
    if (at > s->len) {
        return -1;
    }
    size_t n = strlen(text);
    if (reserve(s, s->len + n) != 0) {
        return -1;
    }
    /* +1 carries the terminator along with the tail. */
    memmove(s->data + at + n, s->data + at, s->len - at + 1);
    memcpy(s->data + at, text, n);
    s->len += n;
    return 0;
}

int str_append(Str *s, const char *text) {
    return str_insert(s, s->len, text);
}

int str_append_char(Str *s, char c) {
    char one[2] = {c, '\0'};
    return str_append(s, one);
}

void str_clear(Str *s) {
    s->len = 0;
    if (s->data != NULL) {
        s->data[0] = '\0';
    }
}

void str_free(Str *s) {
    free(s->data);
    s->data = NULL;
    s->len = 0;
    s->cap = 0;
}
