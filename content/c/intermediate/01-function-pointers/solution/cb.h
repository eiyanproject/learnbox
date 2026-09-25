#ifndef CB_H
#define CB_H

typedef int (*BinaryOp)(int, int);
typedef int (*UnaryOp)(int);

int add_op(int a, int b);
int sub_op(int a, int b);
int mul_op(int a, int b);

BinaryOp find_op(const char *name);
void apply_all(int *values, int n, UnaryOp f);
int reduce(const int *values, int n, int initial, BinaryOp f);
void sort_ints(int *values, int n);

#endif
