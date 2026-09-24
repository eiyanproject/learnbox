#ifndef SHAPE_H
#define SHAPE_H

struct Point {
    int x;
    int y;
};

struct Rect {
    struct Point origin;
    int w;
    int h;
};

struct Point point_of(int x, int y);
void move_point(struct Point *p, int dx, int dy);
int rect_area(const struct Rect *r);
int rect_contains(const struct Rect *r, struct Point p);
struct Rect rect_grow(struct Rect r, int by);

#endif
