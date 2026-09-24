#include "io.h"

#include <stdio.h>
#include <string.h>

int write_lines(const char *path, const char **lines, int n) {
    FILE *f = fopen(path, "w");
    if (f == NULL) {
        return -1;
    }
    int written = 0;
    for (int i = 0; i < n; i++) {
        if (fprintf(f, "%s\n", lines[i]) < 0) {
            fclose(f);
            return -1;
        }
        written++;
    }
    /* Buffered data is flushed here, so a failure at close is a real failure
       to write - reporting success without checking would be a lie. */
    if (fclose(f) != 0) {
        return -1;
    }
    return written;
}

int count_lines(const char *path) {
    FILE *f = fopen(path, "r");
    if (f == NULL) {
        return -1;
    }
    int lines = 0;
    int c;
    int last = '\n';
    while ((c = fgetc(f)) != EOF) {
        if (c == '\n') {
            lines++;
        }
        last = c;
    }
    // A final line with no newline still counts: remembering the last
    // character is the whole of handling that case.
    if (last != '\n') {
        lines++;
    }
    fclose(f);
    return lines;
}

int read_first_line(const char *path, char *buf, int size) {
    if (size <= 0) {
        return -1;
    }
    FILE *f = fopen(path, "r");
    if (f == NULL) {
        return -1;
    }
    if (fgets(buf, size, f) == NULL) {
        fclose(f);
        buf[0] = '\0';
        return -1;
    }
    fclose(f);
    size_t n = strlen(buf);
    if (n > 0 && buf[n - 1] == '\n') {
        buf[n - 1] = '\0'; /* fgets keeps the newline */
        n--;
    }
    return (int)n;
}

int append_line(const char *path, const char *line) {
    FILE *f = fopen(path, "a");
    if (f == NULL) {
        return -1;
    }
    if (fprintf(f, "%s\n", line) < 0) {
        fclose(f);
        return -1;
    }
    return fclose(f) == 0 ? 0 : -1;
}
