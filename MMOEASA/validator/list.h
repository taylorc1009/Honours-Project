#include <stdlib.h>

typedef enum { false, true } bool;

struct ListNode {
    void* value;
    struct ListNode* next;
};

struct List {
    int size;
    struct ListNode* root;
    void (*append)(struct List* restrict, void* restrict);
    void (*clear)(struct List* restrict);
    void* (*at)(struct List* restrict, const int);
};

typedef struct {
    int size;
} init_args;

void append(struct List* restrict self, void* restrict value);
void clear(struct List* restrict self);
void* at(struct List* restrict self, const int index);
struct List* create_list_base(const int size);
struct List* var_init(init_args args);

#define create_list(...) var_init((init_args){__VA_ARGS__});