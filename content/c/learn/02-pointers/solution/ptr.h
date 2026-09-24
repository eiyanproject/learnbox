#ifndef PTR_H
#define PTR_H

void swap(int *a, int *b);
void sum_and_count(const int *values, int n, int *sum_out, int *count_out);
int find_index(const int *values, int n, int target);
void increment_all(int *values, int n);

#endif
