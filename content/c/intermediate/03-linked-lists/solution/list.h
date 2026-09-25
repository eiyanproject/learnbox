#ifndef LIST_H
#define LIST_H

struct Node {
    int value;
    struct Node *next;
};

struct List {
    struct Node *head;
    int count;
};

void list_init(struct List *list);
int list_push_front(struct List *list, int value);
int list_push_back(struct List *list, int value);
int list_contains(const struct List *list, int value);
int list_remove(struct List *list, int value);
void list_free(struct List *list);

#endif
