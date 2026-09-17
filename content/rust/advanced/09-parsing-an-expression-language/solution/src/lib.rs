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
    let mut tokens = Vec::new();
    let mut chars = input.char_indices().peekable();
    while let Some(&(pos, c)) = chars.peek() {
        match c {
            ' ' | '\t' | '\n' => {
                chars.next();
            }
            '0'..='9' | '.' => {
                let mut text = String::new();
                while let Some(&(_, d)) = chars.peek() {
                    if d.is_ascii_digit() || d == '.' {
                        text.push(d);
                        chars.next();
                    } else {
                        break;
                    }
                }
                let n = text.parse::<f64>().map_err(|_| ParseError::InvalidNumber(text.clone()))?;
                tokens.push(Token::Num(n));
            }
            _ => {
                let token = match c {
                    '+' => Token::Plus,
                    '-' => Token::Minus,
                    '*' => Token::Star,
                    '/' => Token::Slash,
                    '(' => Token::LParen,
                    ')' => Token::RParen,
                    other => return Err(ParseError::UnexpectedChar(other, pos)),
                };
                tokens.push(token);
                chars.next();
            }
        }
    }
    Ok(tokens)
}

struct Parser<'a> {
    tokens: &'a [Token],
    pos: usize,
}

impl<'a> Parser<'a> {
    fn peek(&self) -> Option<&'a Token> {
        self.tokens.get(self.pos)
    }

    fn next(&mut self) -> Result<Token, ParseError> {
        let t = self.tokens.get(self.pos).cloned().ok_or(ParseError::UnexpectedEnd)?;
        self.pos += 1;
        Ok(t)
    }

    fn expr(&mut self) -> Result<Expr, ParseError> {
        let mut left = self.term()?;
        while let Some(Token::Plus | Token::Minus) = self.peek() {
            let op = self.next()?;
            let right = self.term()?;
            left = Expr::Binary(Box::new(left), op, Box::new(right));
        }
        Ok(left)
    }

    fn term(&mut self) -> Result<Expr, ParseError> {
        let mut left = self.factor()?;
        while let Some(Token::Star | Token::Slash) = self.peek() {
            let op = self.next()?;
            let right = self.factor()?;
            left = Expr::Binary(Box::new(left), op, Box::new(right));
        }
        Ok(left)
    }

    fn factor(&mut self) -> Result<Expr, ParseError> {
        match self.next()? {
            Token::Num(n) => Ok(Expr::Num(n)),
            Token::Minus => Ok(Expr::Neg(Box::new(self.factor()?))),
            Token::LParen => {
                let inner = self.expr()?;
                match self.next()? {
                    Token::RParen => Ok(inner),
                    other => Err(ParseError::UnexpectedToken(other)),
                }
            }
            other => Err(ParseError::UnexpectedToken(other)),
        }
    }
}

pub fn parse(tokens: &[Token]) -> Result<Expr, ParseError> {
    let mut parser = Parser { tokens, pos: 0 };
    let expr = parser.expr()?;
    if parser.pos != tokens.len() {
        return Err(ParseError::TrailingInput);
    }
    Ok(expr)
}

pub fn eval(expr: &Expr) -> Result<f64, EvalError> {
    Ok(match expr {
        Expr::Num(n) => *n,
        Expr::Neg(inner) => -eval(inner)?,
        Expr::Binary(l, op, r) => {
            let (a, b) = (eval(l)?, eval(r)?);
            match op {
                Token::Plus => a + b,
                Token::Minus => a - b,
                Token::Star => a * b,
                Token::Slash if b == 0.0 => return Err(EvalError::DivisionByZero),
                Token::Slash => a / b,
                _ => unreachable!("the parser only builds arithmetic operators"),
            }
        }
    })
}

pub fn calculate(input: &str) -> Result<f64, String> {
    let tokens = tokenize(input).map_err(|e| format!("{e:?}"))?;
    let expr = parse(&tokens).map_err(|e| format!("{e:?}"))?;
    eval(&expr).map_err(|e| format!("{e:?}"))
}
