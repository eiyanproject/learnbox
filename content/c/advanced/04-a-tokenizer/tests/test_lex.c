#include "ctest.h"
#include "lex.h"

#include <string.h>

TEST(an_empty_input_is_immediately_the_end) {
    struct Lexer lex;
    lex_init(&lex, "");
    ASSERT_EQ_INT(TOK_END, lex_next(&lex).kind);
}

TEST(whitespace_only_is_the_end) {
    struct Lexer lex;
    lex_init(&lex, "   \t  ");
    ASSERT_EQ_INT(TOK_END, lex_next(&lex).kind);
}

TEST(reads_a_number) {
    struct Lexer lex;
    lex_init(&lex, "123");
    struct Token t = lex_next(&lex);
    ASSERT_EQ_INT(TOK_NUMBER, t.kind);
    ASSERT_EQ_INT(123, (int)t.value);
    ASSERT_EQ_INT(3, t.length);
}

TEST(reads_an_identifier) {
    struct Lexer lex;
    lex_init(&lex, "total_1");
    struct Token t = lex_next(&lex);
    ASSERT_EQ_INT(TOK_IDENT, t.kind);
    ASSERT_EQ_INT(7, t.length);
}

TEST(an_identifier_may_start_with_an_underscore) {
    struct Lexer lex;
    lex_init(&lex, "_x");
    ASSERT_EQ_INT(TOK_IDENT, lex_next(&lex).kind);
}

TEST(a_number_is_not_an_identifier) {
    /* If identifiers were checked first, "123" would lex as a name. */
    struct Lexer lex;
    lex_init(&lex, "123abc");
    ASSERT_EQ_INT(TOK_NUMBER, lex_next(&lex).kind);
    ASSERT_EQ_INT(TOK_IDENT, lex_next(&lex).kind);
}

TEST(the_token_points_into_the_input) {
    const char *input = "  abc";
    struct Lexer lex;
    lex_init(&lex, input);
    struct Token t = lex_next(&lex);
    ASSERT_TRUE(t.start == input + 2);
    ASSERT_EQ_INT(0, strncmp(t.start, "abc", 3));
}

TEST(reads_the_operators) {
    struct Lexer lex;
    lex_init(&lex, "+-*/()");
    ASSERT_EQ_INT(TOK_PLUS, lex_next(&lex).kind);
    ASSERT_EQ_INT(TOK_MINUS, lex_next(&lex).kind);
    ASSERT_EQ_INT(TOK_STAR, lex_next(&lex).kind);
    ASSERT_EQ_INT(TOK_SLASH, lex_next(&lex).kind);
    ASSERT_EQ_INT(TOK_LPAREN, lex_next(&lex).kind);
    ASSERT_EQ_INT(TOK_RPAREN, lex_next(&lex).kind);
}

TEST(whitespace_between_tokens_is_skipped) {
    struct Lexer lex;
    lex_init(&lex, "  1  +  2  ");
    ASSERT_EQ_INT(TOK_NUMBER, lex_next(&lex).kind);
    ASSERT_EQ_INT(TOK_PLUS, lex_next(&lex).kind);
    ASSERT_EQ_INT(TOK_NUMBER, lex_next(&lex).kind);
    ASSERT_EQ_INT(TOK_END, lex_next(&lex).kind);
}

TEST(an_unknown_character_is_an_error) {
    struct Lexer lex;
    lex_init(&lex, "1 $ 2");
    lex_next(&lex);
    ASSERT_EQ_INT(TOK_ERROR, lex_next(&lex).kind);
}

TEST(counting_a_whole_expression) {
    ASSERT_EQ_INT(7, lex_count("(1 + 23) * total"));
}

TEST(counting_an_empty_input) {
    ASSERT_EQ_INT(0, lex_count(""));
}

TEST(counting_reports_an_error) {
    ASSERT_EQ_INT(-1, lex_count("1 # 2"));
}

CTEST_MAIN
