#ifndef EVAL_H
#define EVAL_H

#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <variant>
#include <vector>

struct ParseError : std::runtime_error {
    using std::runtime_error::runtime_error;
};

struct Token {
    enum class Kind { Number, Op, LParen, RParen };
    Kind kind;
    double value = 0; // Number only
    char op = 0;      // Op only
};

inline std::vector<Token> tokenize(std::string_view text) {
    std::vector<Token> tokens;
    std::size_t i = 0;
    while (i < text.size()) {
        char c = text[i];
        if (c == ' ' || c == '\t') {
            ++i;
            continue;
        }
        if (c >= '0' && c <= '9') {
            double value = 0;
            while (i < text.size() && text[i] >= '0' && text[i] <= '9') {
                value = value * 10 + (text[i] - '0');
                ++i;
            }
            if (i < text.size() && text[i] == '.') {
                ++i;
                double scale = 0.1;
                while (i < text.size() && text[i] >= '0' && text[i] <= '9') {
                    value += (text[i] - '0') * scale;
                    scale /= 10;
                    ++i;
                }
            }
            tokens.push_back({Token::Kind::Number, value, 0});
            continue;
        }
        if (c == '+' || c == '-' || c == '*' || c == '/') {
            tokens.push_back({Token::Kind::Op, 0, c});
            ++i;
            continue;
        }
        if (c == '(') {
            tokens.push_back({Token::Kind::LParen, 0, 0});
            ++i;
            continue;
        }
        if (c == ')') {
            tokens.push_back({Token::Kind::RParen, 0, 0});
            ++i;
            continue;
        }
        throw ParseError(std::string("unexpected character: ") + c);
    }
    return tokens;
}

struct Node;

struct Num {
    double value;
};

struct Binary {
    char op;
    std::unique_ptr<Node> lhs;
    std::unique_ptr<Node> rhs;
};

// A variant cannot contain itself, so the recursion goes through the pointers
// in Binary rather than through the variant.
struct Node {
    std::variant<Num, Binary> value;
};

namespace detail {

class Parser {
public:
    explicit Parser(std::vector<Token> tokens) : tokens_(std::move(tokens)) {}

    std::unique_ptr<Node> parse_all() {
        auto root = expr();
        if (pos_ != tokens_.size()) {
            throw ParseError("trailing input");
        }
        return root;
    }

private:
    const Token* peek() const {
        return pos_ < tokens_.size() ? &tokens_[pos_] : nullptr;
    }

    static std::unique_ptr<Node> make_binary(char op, std::unique_ptr<Node> lhs,
                                             std::unique_ptr<Node> rhs) {
        return std::make_unique<Node>(Node{Binary{op, std::move(lhs), std::move(rhs)}});
    }

    // expr := term (('+' | '-') term)*   - the loop is what makes it left associative
    std::unique_ptr<Node> expr() {
        auto lhs = term();
        while (const Token* t = peek()) {
            if (t->kind != Token::Kind::Op || (t->op != '+' && t->op != '-')) {
                break;
            }
            char op = t->op;
            ++pos_;
            lhs = make_binary(op, std::move(lhs), term());
        }
        return lhs;
    }

    // term := factor (('*' | '/') factor)*
    std::unique_ptr<Node> term() {
        auto lhs = factor();
        while (const Token* t = peek()) {
            if (t->kind != Token::Kind::Op || (t->op != '*' && t->op != '/')) {
                break;
            }
            char op = t->op;
            ++pos_;
            lhs = make_binary(op, std::move(lhs), factor());
        }
        return lhs;
    }

    // factor := '-' factor | number | '(' expr ')'
    std::unique_ptr<Node> factor() {
        const Token* t = peek();
        if (t == nullptr) {
            throw ParseError("unexpected end of input");
        }
        if (t->kind == Token::Kind::Op && t->op == '-') {
            ++pos_;
            return make_binary('-', std::make_unique<Node>(Node{Num{0}}), factor());
        }
        if (t->kind == Token::Kind::Number) {
            double value = t->value;
            ++pos_;
            return std::make_unique<Node>(Node{Num{value}});
        }
        if (t->kind == Token::Kind::LParen) {
            ++pos_;
            auto inner = expr();
            const Token* close = peek();
            if (close == nullptr || close->kind != Token::Kind::RParen) {
                throw ParseError("expected )");
            }
            ++pos_;
            return inner;
        }
        throw ParseError("expected a number");
    }

    std::vector<Token> tokens_;
    std::size_t pos_ = 0;
};

template <typename... Ts>
struct overloaded : Ts... {
    using Ts::operator()...;
};
template <typename... Ts>
overloaded(Ts...) -> overloaded<Ts...>;

} // namespace detail

inline std::unique_ptr<Node> parse(std::string_view text) {
    detail::Parser parser(tokenize(text));
    return parser.parse_all();
}

inline double eval(const Node& node) {
    // std::visit refuses to compile if an alternative is left unhandled.
    return std::visit(
        detail::overloaded{
            [](const Num& n) { return n.value; },
            [](const Binary& b) {
                double lhs = eval(*b.lhs);
                double rhs = eval(*b.rhs);
                switch (b.op) {
                case '+':
                    return lhs + rhs;
                case '-':
                    return lhs - rhs;
                case '*':
                    return lhs * rhs;
                case '/':
                    if (rhs == 0) {
                        throw ParseError("division by zero");
                    }
                    return lhs / rhs;
                default:
                    throw ParseError("unknown operator");
                }
            },
        },
        node.value);
}

inline std::optional<double> evaluate(std::string_view text) {
    // The caller asked whether the text is a valid expression; being told "no"
    // is an answer, not an exception.
    try {
        return eval(*parse(text));
    } catch (const ParseError&) {
        return std::nullopt;
    }
}

#endif
