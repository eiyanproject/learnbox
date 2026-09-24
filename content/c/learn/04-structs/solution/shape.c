#include "shape.h"

struct Point point_of(int x, int y) {
    struct Point p = {x, y};
    return p;
}

void move_point(struct Point *p, int dx, int dy) {
    p->x += dx;
    p->y += dy;
}

int rect_area(const struct Rect *r) {
    return r->w * r->h;
}

int rect_contains(const struct Rect *r, struct Point p) {
    /* Origin inclusive, far edge exclusive: the same convention as array
       indices, and it makes adjacent rects tile without overlapping. */
    return p.x >= r->origin.x && p.x < r->origin.x + r->w
        && p.y >= r->origin.y && p.y < r->origin.y + r->h;
}

struct Rect rect_grow(struct Rect r, int by) {
    r.w += by; /* r is our own copy: changing it cannot affect the caller */
    r.h += by;
    return r;
}
