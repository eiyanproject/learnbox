#include "ctest.h"
#include "eval.h"

#include <string>

TEST(tokenizes_a_number) {
    auto tokens = tokenize("42");
    ASSERT_EQ_INT(1, (int)tokens.size());
    ASSERT_TRUE(tokens[0].kind == Token::Kind::Number);
    ASSERT_NEAR(42.0, tokens[0].value, 1e-9);
}

TEST(tokenizes_operators_and_parens) {
    auto tokens = tokenize("1+(2)");
    ASSERT_EQ_INT(5, (int)tokens.size());
    ASSERT_TRUE(tokens[1].kind == Token::Kind::Op);
    ASSERT_EQ_INT((int)'+', (int)tokens[1].op);
    ASSERT_TRUE(tokens[2].kind == Token::Kind::LParen);
    ASSERT_TRUE(tokens[4].kind == Token::Kind::RParen);
}

TEST(whitespace_is_skipped) {
    ASSERT_EQ_INT(3, (int)tokenize("  1 +   2 ").size());
}

TEST(an_unexpected_character_is_a_parse_error) {
    bool threw = false;
    try {
        tokenize("1 $ 2");
    } catch (const ParseError&) {
        threw = true;
    }
    ASSERT_TRUE(threw);
}

TEST(evaluates_a_bare_number) {
    ASSERT_NEAR(7.0, *evaluate("7"), 1e-9);
}

TEST(evaluates_addition_and_subtraction) {
    ASSERT_NEAR(6.0, *evaluate("1 + 2 + 3"), 1e-9);
    ASSERT_NEAR(4.0, *evaluate("9 - 5"), 1e-9);
}

TEST(subtraction_is_left_associative) {
    /* (8 - 3) - 2, not 8 - (3 - 2). */
    ASSERT_NEAR(3.0, *evaluate("8 - 3 - 2"), 1e-9);
}

TEST(division_is_left_associative) {
    ASSERT_NEAR(2.0, *evaluate("16 / 4 / 2"), 1e-9);
}

TEST(multiplication_binds_tighter_than_addition) {
    ASSERT_NEAR(14.0, *evaluate("2 + 3 * 4"), 1e-9);
    ASSERT_NEAR(14.0, *evaluate("3 * 4 + 2"), 1e-9);
}

TEST(parentheses_override_precedence) {
    ASSERT_NEAR(20.0, *evaluate("(2 + 3) * 4"), 1e-9);
    ASSERT_NEAR(11.0, *evaluate("2 + 3 * (4 - 1)"), 1e-9);
}

TEST(nested_parentheses) {
    ASSERT_NEAR(18.0, *evaluate("2 * ((1 + 2) * (4 - 1))"), 1e-9);
}

TEST(unary_minus) {
    ASSERT_NEAR(-5.0, *evaluate("-5"), 1e-9);
    ASSERT_NEAR(1.0, *evaluate("-2 + 3"), 1e-9);
    ASSERT_NEAR(-6.0, *evaluate("-(2 * 3)"), 1e-9);
}

TEST(decimals) {
    ASSERT_NEAR(3.5, *evaluate("1.25 + 2.25"), 1e-9);
}

TEST(division_by_zero_has_no_value) {
    ASSERT_FALSE(evaluate("1 / 0").has_value());
}

TEST(an_unbalanced_paren_has_no_value) {
    ASSERT_FALSE(evaluate("(1 + 2").has_value());
    ASSERT_FALSE(evaluate("1 + 2)").has_value());
}

TEST(a_dangling_operator_has_no_value) {
    ASSERT_FALSE(evaluate("1 +").has_value());
    ASSERT_FALSE(evaluate("").has_value());
}

TEST(garbage_has_no_value) {
    ASSERT_FALSE(evaluate("1 $ 2").has_value());
}

TEST(the_tree_holds_the_structure) {
    auto root = parse("1 + 2");
    ASSERT_TRUE(std::holds_alternative<Binary>(root->value));
    const auto& top = std::get<Binary>(root->value);
    ASSERT_EQ_INT((int)'+', (int)top.op);
    ASSERT_TRUE(std::holds_alternative<Num>(top.lhs->value));
    ASSERT_NEAR(1.0, std::get<Num>(top.lhs->value).value, 1e-9);
}

TEST(the_tree_shape_shows_the_precedence) {
    /* 2 + 3 * 4 must be a '+' at the root with a '*' on the right. */
    auto root = parse("2 + 3 * 4");
    const auto& top = std::get<Binary>(root->value);
    ASSERT_EQ_INT((int)'+', (int)top.op);
    ASSERT_TRUE(std::holds_alternative<Binary>(top.rhs->value));
    ASSERT_EQ_INT((int)'*', (int)std::get<Binary>(top.rhs->value).op);
}

TEST(eval_can_be_called_on_a_parsed_tree_directly) {
    auto root = parse("(1 + 1) * 5");
    ASSERT_NEAR(10.0, eval(*root), 1e-9);
}

CTEST_MAIN
