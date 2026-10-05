#[derive(Debug, PartialEq, Eq)]
pub enum EvalError {
    StackUnderflow,
    DivisionByZero,
    UnknownToken(String),
    LeftOver(usize),
}

pub fn eval(program: &str) -> Result<i64, EvalError> {
    todo!()
}
