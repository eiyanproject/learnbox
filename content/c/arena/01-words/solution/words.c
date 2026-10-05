#include "words.h"

#include <ctype.h>
#include <string.h>

int count_words(const char *s) {
    int count = 0;
    int in_word = 0;
    for (; *s; s++) {
        if (isspace((unsigned char)*s)) {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            count++;
        }
    }
    return count;
}

int trim(char *s) {
    size_t start = 0;
    size_t end = strlen(s);
    while (s[start] && isspace((unsigned char)s[start])) {
        start++;
    }
    while (end > start && isspace((unsigned char)s[end - 1])) {
        end--;
    }
    memmove(s, s + start, end - start);
    s[end - start] = '\0';
    return (int)(end - start);
}
