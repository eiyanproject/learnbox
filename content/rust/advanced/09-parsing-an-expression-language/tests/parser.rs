use expression_parser::*;

#[test]
fn tokens() {
    assert_eq!(
        tokenize("2 * (3 + 4.5)").unwrap(),
        [Token::Num(2.0), Token::Star, Token::LParen, Token::Num(3.0), Token::Plus, Token::Num(4.5), Token::RParen]
    );
    assert_eq!(tokenize("   ").unwrap(), []);
}

#[test]
fn tokenizer_errors() {
    assert_eq!(tokenize("1 + $"), Err(ParseError::UnexpectedChar('$', 4)));
    assert_eq!(tokenize("1.2.3"), Err(ParseError::InvalidNumber("1.2.3".into())));
}

#[test]
fn precedence_and_associativity() {
    assert_eq!(calculate("1 + 2 * 3"), Ok(7.0));
    assert_eq!(calculate("(1 + 2) * 3"), Ok(9.0));
    assert_eq!(calculate("8 - 3 - 2"), Ok(3.0));
    assert_eq!(calculate("16 / 4 / 2"), Ok(2.0));
    assert_eq!(calculate("2 * 3 + 4 * 5"), Ok(26.0));
}

#[test]
fn unary_minus_and_decimals() {
    assert_eq!(calculate("-3 + 5"), Ok(2.0));
    assert_eq!(calculate("--4"), Ok(4.0));
    assert_eq!(calculate("-(1.5 * 2)"), Ok(-3.0));
    assert_eq!(calculate("0.1 + 0.2 * 10"), Ok(2.1));
}

#[test]
fn tree_shape() {
    let tree = parse(&tokenize("1 - 2 - 3").unwrap()).unwrap();
    let expected = Expr::Binary(
        Box::new(Expr::Binary(Box::new(Expr::Num(1.0)), Token::Minus, Box::new(Expr::Num(2.0)))),
        Token::Minus,
        Box::new(Expr::Num(3.0)),
    );
    assert_eq!(tree, expected);
}

#[test]
fn parse_errors() {
    assert_eq!(parse(&tokenize("1 +").unwrap()), Err(ParseError::UnexpectedEnd));
    assert_eq!(parse(&tokenize("(1 + 2").unwrap()), Err(ParseError::UnexpectedEnd));
    assert_eq!(parse(&tokenize("* 2").unwrap()), Err(ParseError::UnexpectedToken(Token::Star)));
    assert_eq!(parse(&tokenize("1 2").unwrap()), Err(ParseError::TrailingInput));
    assert_eq!(parse(&tokenize("(1))").unwrap()), Err(ParseError::TrailingInput));
    assert_eq!(parse(&[]), Err(ParseError::UnexpectedEnd));
}

#[test]
fn evaluation_errors() {
    assert_eq!(calculate("1 / (2 - 2)"), Err("DivisionByZero".to_string()));
    assert_eq!(calculate("1 + #"), Err("UnexpectedChar('#', 4)".to_string()));
}
