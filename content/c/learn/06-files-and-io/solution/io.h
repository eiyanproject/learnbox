#ifndef IO_H
#define IO_H

int write_lines(const char *path, const char **lines, int n);
int count_lines(const char *path);
int read_first_line(const char *path, char *buf, int size);
int append_line(const char *path, const char *line);

#endif
