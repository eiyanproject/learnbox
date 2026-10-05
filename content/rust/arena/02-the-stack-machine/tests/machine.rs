use arena_stack_machine::*;

#[test]
fn a_number_is_a_program() {
    assert_eq!(eval("42"), Ok(42));
    assert_eq!(eval("-7"), Ok(-7));
}

#[test]
fn arithmetic() {
    assert_eq!(eval("2 3 +"), Ok(5));
    assert_eq!(eval("2 3 + 4 *"), Ok(20));
}

#[test]
fn operands_come_in_order() {
    assert_eq!(eval("10 2 -"), Ok(8));
    assert_eq!(eval("2 10 -"), Ok(-8));
    assert_eq!(eval("7 2 /"), Ok(3));
    assert_eq!(eval("-7 2 /"), Ok(-3));
}

#[test]
fn whitespace_is_just_a_separator() {
    assert_eq!(eval("  2\t3\n+  "), Ok(5));
}

#[test]
fn dup_swap_drop() {
    assert_eq!(eval("3 dup *"), Ok(9));
    assert_eq!(eval("2 10 swap -"), Ok(8));
    assert_eq!(eval("1 2 drop"), Ok(1));
    assert_eq!(eval("5 dup dup + +"), Ok(15));
}

#[test]
fn minus_alone_is_an_operator_not_a_number() {
    assert_eq!(eval("5 3 - -2 -"), Ok(4));
}

#[test]
fn underflow() {
    assert_eq!(eval("+"), Err(EvalError::StackUnderflow));
    assert_eq!(eval("1 +"), Err(EvalError::StackUnderflow));
    assert_eq!(eval("dup"), Err(EvalError::StackUnderflow));
    assert_eq!(eval("1 swap"), Err(EvalError::StackUnderflow));
    assert_eq!(eval("drop"), Err(EvalError::StackUnderflow));
}

#[test]
fn an_empty_stack_at_the_end_is_underflow() {
    assert_eq!(eval(""), Err(EvalError::StackUnderflow));
    assert_eq!(eval("   "), Err(EvalError::StackUnderflow));
    assert_eq!(eval("1 drop"), Err(EvalError::StackUnderflow));
}

#[test]
fn division_by_zero() {
    assert_eq!(eval("1 0 /"), Err(EvalError::DivisionByZero));
    assert_eq!(eval("4 2 2 - /"), Err(EvalError::DivisionByZero));
}

#[test]
fn unknown_tokens_are_named() {
    assert_eq!(eval("1 2 plus"), Err(EvalError::UnknownToken("plus".to_string())));
    assert_eq!(eval("1.5"), Err(EvalError::UnknownToken("1.5".to_string())));
    assert_eq!(eval("DUP"), Err(EvalError::UnknownToken("DUP".to_string())));
}

#[test]
fn left_over_values_are_counted() {
    assert_eq!(eval("1 2"), Err(EvalError::LeftOver(2)));
    assert_eq!(eval("1 2 3 +"), Err(EvalError::LeftOver(2)));
    assert_eq!(eval("1 dup dup"), Err(EvalError::LeftOver(3)));
}

#[test]
fn the_first_error_wins() {
    assert_eq!(eval("+ nonsense"), Err(EvalError::StackUnderflow));
    assert_eq!(eval("nonsense +"), Err(EvalError::UnknownToken("nonsense".to_string())));
    assert_eq!(eval("1 0 / +"), Err(EvalError::DivisionByZero));
}
