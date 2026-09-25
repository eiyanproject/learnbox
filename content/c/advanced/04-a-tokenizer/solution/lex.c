#include "lex.h"

#include <ctype.h>

void lex_init(struct Lexer *lex, const char *input) {
    lex->input = input;
    lex->pos = 0;
}

static char peek(const struct Lexer *lex) {
    return lex->input[lex->pos];
}

static struct Token make(enum TokenKind kind, const char *start, int length) {
    struct Token t;
    t.kind = kind;
    t.start = start;
    t.length = length;
    t.value = 0;
    return t;
}

struct Token lex_next(struct Lexer *lex) {
    /* The cast matters: a plain char is signed here, and isspace on a
       negative value other than EOF is undefined. */
    while (peek(lex) != '\0' && isspace((unsigned char)peek(lex))) {
        lex->pos++;
    }

    const char *start = lex->input + lex->pos;
    char c = peek(lex);
    if (c == '\0') {
        return make(TOK_END, start, 0);
    }

    /* Digits before identifiers, or "123" starts looking like a name. */
    if (isdigit((unsigned char)c)) {
        long value = 0;
        int length = 0;
        while (isdigit((unsigned char)peek(lex))) {
            value = value * 10 + (peek(lex) - '0');
            lex->pos++;
            length++;
        }
        struct Token t = make(TOK_NUMBER, start, length);
        t.value = value;
        return t;
    }

    if (isalpha((unsigned char)c) || c == '_') {
        int length = 0;
        while (isalnum((unsigned char)peek(lex)) || peek(lex) == '_') {
            lex->pos++;
            length++;
        }
        return make(TOK_IDENT, start, length);
    }

    lex->pos++;
    switch (c) {
        case '+': return make(TOK_PLUS, start, 1);
        case '-': return make(TOK_MINUS, start, 1);
        case '*': return make(TOK_STAR, start, 1);
        case '/': return make(TOK_SLASH, start, 1);
        case '(': return make(TOK_LPAREN, start, 1);
        case ')': return make(TOK_RPAREN, start, 1);
        default:  return make(TOK_ERROR, start, 1);
    }
}

int lex_count(const char *input) {
    struct Lexer lex;
    lex_init(&lex, input);
    int count = 0;
    for (;;) {
        struct Token t = lex_next(&lex);
        if (t.kind == TOK_END) {
            return count;
        }
        if (t.kind == TOK_ERROR) {
            return -1;
        }
        count++;
    }
}
