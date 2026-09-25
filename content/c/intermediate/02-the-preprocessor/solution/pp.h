#ifndef PP_H
#define PP_H

/* Parentheses around each parameter AND around the whole body: the first
   fixes argument precedence, the second fixes how the result combines with
   whatever surrounds the macro. */
#define SQUARE(x) ((x) * (x))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))

/* Only correct where the real array type is visible: on a pointer this gives
   the size of the pointer divided by the size of an element. */
#define ARRAY_LEN(a) (sizeof(a) / sizeof((a)[0]))

#define CLAMP(v, lo, hi) (MAX((lo), MIN((v), (hi))))

/* The function version: each argument is evaluated exactly once. */
int safe_max(int a, int b);

#endif
