#include <stdio.h>
#include "list.h"

typedef struct {
    char* file;
} io_args;

bool inline is_num_end(const int c);
void inline read_float(FILE* restrict file, float* restrict var);
struct Solution* read_csv_base(char* restrict filename);
struct Solution* var_io(io_args in);

#define read_csv(...) var_io((io_args){__VA_ARGS__})