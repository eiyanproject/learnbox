use std::collections::HashMap;

pub struct EventBus {
    // handlers: ...
}

impl EventBus {
    pub fn new() -> Self {
        todo!()
    }

    // on, emit, handler_count
}

pub fn make_counter() -> impl FnMut() -> u32 {
    || todo!()
}

// The bound is too strict: FnMut closures should be accepted.
pub fn apply_twice<F: Fn(i32) -> i32>(f: F, x: i32) -> i32 {
    f(f(x))
}

// The bound is too strict: FnOnce closures should be accepted.
pub fn run_once<F: Fn() -> String>(f: F) -> String {
    f()
}

pub fn compose<F, G>(f: F, g: G) -> impl Fn(i32) -> i32
where
    F: Fn(i32) -> i32,
    G: Fn(i32) -> i32,
{
    move |x| todo!("compose {x}")
}
