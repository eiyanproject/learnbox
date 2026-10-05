#ifndef STR_H
#define STR_H

#include <stddef.h>

typedef struct {
    char *data;   /* heap buffer, always NUL-terminated */
    size_t len;   /* characters in the string, not counting the terminator */
    size_t cap;   /* bytes allocated; always greater than len */
} Str;

int str_init(Str *s);
int str_append(Str *s, const char *text);
int str_append_char(Str *s, char c);
int str_insert(Str *s, size_t at, const char *text);
void str_clear(Str *s);
void str_free(Str *s);

#endif
