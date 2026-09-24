#ifndef NUMS_H
#define NUMS_H

int type_size(const char *name);
int safe_add(int a, int b, int *out);
unsigned wrap_add(unsigned a, unsigned b);
int truncate_to_char(int value);

#endif
