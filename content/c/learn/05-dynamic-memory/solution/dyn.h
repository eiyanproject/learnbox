#ifndef DYN_H
#define DYN_H

/* Each of these returns memory the CALLER is responsible for freeing,
   except sum_and_free, which takes ownership and frees it. */

int *make_range(int n);
char *dup_string(const char *s);
int *grow_array(int *values, int old_n, int new_n);
int sum_and_free(int *values, int n);

#endif
