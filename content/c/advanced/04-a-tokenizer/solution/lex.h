#ifndef LEX_H
#define LEX_H

enum TokenKind {
    TOK_END,
    TOK_NUMBER,
    TOK_IDENT,
    TOK_PLUS,
    TOK_MINUS,
    TOK_STAR,
    TOK_SLASH,
    TOK_LPAREN,
    TOK_RPAREN,
    TOK_ERROR
};

struct Token {
    enum TokenKind kind;
    const char *start; /* points into the input, which must outlive the token */
    int length;
    long value;
};

struct Lexer {
    const char *input;
    int pos;
};

void lex_init(struct Lexer *lex, const char *input);
struct Token lex_next(struct Lexer *lex);
int lex_count(const char *input);

#endif
