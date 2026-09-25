#include "list.h"

#include <stdlib.h>

void list_init(struct List *list) {
    list->head = NULL;
    list->count = 0;
}

int list_push_front(struct List *list, int value) {
    struct Node *node = malloc(sizeof *node);
    if (node == NULL) {
        return 0;
    }
    node->value = value;
    node->next = list->head;
    list->head = node;
    list->count++;
    return 1;
}

int list_push_back(struct List *list, int value) {
    struct Node *node = malloc(sizeof *node);
    if (node == NULL) {
        return 0;
    }
    node->value = value;
    node->next = NULL;

    /* The same pointer-to-pointer idea: walk to the NULL at the end and write
       through whatever pointer holds it, head included. */
    struct Node **link = &list->head;
    while (*link != NULL) {
        link = &(*link)->next;
    }
    *link = node;
    list->count++;
    return 1;
}

int list_contains(const struct List *list, int value) {
    for (const struct Node *n = list->head; n != NULL; n = n->next) {
        if (n->value == value) {
            return 1;
        }
    }
    return 0;
}

int list_remove(struct List *list, int value) {
    struct Node **link = &list->head;
    while (*link != NULL && (*link)->value != value) {
        link = &(*link)->next;
    }
    if (*link == NULL) {
        return 0;
    }
    /* *link is the head pointer on the first iteration and a node's next
       field afterwards, so there is no special case for removing the head. */
    struct Node *dead = *link;
    *link = dead->next;
    free(dead);
    list->count--;
    return 1;
}

void list_free(struct List *list) {
    struct Node *node = list->head;
    while (node != NULL) {
        struct Node *next = node->next; /* saved before the free */
        free(node);
        node = next;
    }
    list_init(list);
}
