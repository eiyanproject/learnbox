#ifndef BITS_H
#define BITS_H

#define FLAG_READ  (1u << 0)
#define FLAG_WRITE (1u << 1)
#define FLAG_EXEC  (1u << 2)

unsigned set_flag(unsigned value, unsigned flag);
unsigned clear_flag(unsigned value, unsigned flag);
unsigned toggle_flag(unsigned value, unsigned flag);
int has_flag(unsigned value, unsigned flag);
int count_bits(unsigned value);
unsigned extract_byte(unsigned value, int index);

#endif
