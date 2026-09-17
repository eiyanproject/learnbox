#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    Num(f64),
    Plus,
    Minus,
    Star,
    Slash,
    LParen,
    RParen,
}

#[derive(Debug, PartialEq)]
pub enum ParseError {
    UnexpectedChar(char, usize),
    InvalidNumber(String),
    UnexpectedEnd,
    UnexpectedToken(Token),
    TrailingInput,
}

#[derive(Debug, PartialEq)]
pub enum EvalError {
    DivisionByZero,
}

#[derive(Debug, PartialEq)]
pub enum Expr {
    Num(f64),
    Neg(Box<Expr>),
    Binary(Box<Expr>, Token, Box<Expr>),
}

pub fn tokenize(input: &str) -> Result<Vec<Token>, ParseError> {
    todo!()
}

pub fn parse(tokens: &[Token]) -> Result<Expr, ParseError> {
    todo!()
}

pub fn eval(expr: &Expr) -> Result<f64, EvalError> {
    todo!()
}

pub fn calculate(input: &str) -> Result<f64, String> {
    let tokens = tokenize(input).map_err(|e| format!("{e:?}"))?;
    let expr = parse(&tokens).map_err(|e| format!("{e:?}"))?;
    eval(&expr).map_err(|e| format!("{e:?}"))
}
