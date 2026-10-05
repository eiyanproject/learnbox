#[derive(Debug, PartialEq, Eq)]
pub enum EvalError {
    StackUnderflow,
    DivisionByZero,
    UnknownToken(String),
    LeftOver(usize),
}

fn pop(stack: &mut Vec<i64>) -> Result<i64, EvalError> {
    stack.pop().ok_or(EvalError::StackUnderflow)
}

pub fn eval(program: &str) -> Result<i64, EvalError> {
    let mut stack: Vec<i64> = Vec::new();
    for token in program.split_whitespace() {
        if let Ok(n) = token.parse::<i64>() {
            stack.push(n);
            continue;
        }
        match token {
            "+" | "-" | "*" | "/" => {
                let b = pop(&mut stack)?;
                let a = pop(&mut stack)?;
                stack.push(match token {
                    "+" => a + b,
                    "-" => a - b,
                    "*" => a * b,
                    _ if b == 0 => return Err(EvalError::DivisionByZero),
                    _ => a / b,
                });
            }
            "dup" => {
                let top = pop(&mut stack)?;
                stack.push(top);
                stack.push(top);
            }
            "swap" => {
                let b = pop(&mut stack)?;
                let a = pop(&mut stack)?;
                stack.push(b);
                stack.push(a);
            }
            "drop" => {
                pop(&mut stack)?;
            }
            other => return Err(EvalError::UnknownToken(other.to_string())),
        }
    }
    match stack.len() {
        0 => Err(EvalError::StackUnderflow),
        1 => Ok(stack[0]),
        n => Err(EvalError::LeftOver(n)),
    }
}
