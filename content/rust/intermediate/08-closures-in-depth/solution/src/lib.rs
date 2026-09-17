use std::collections::HashMap;

pub struct EventBus {
    handlers: HashMap<String, Vec<Box<dyn Fn(&str) -> String>>>,
}

impl EventBus {
    pub fn new() -> Self {
        EventBus { handlers: HashMap::new() }
    }

    pub fn on(&mut self, event: &str, handler: impl Fn(&str) -> String + 'static) {
        self.handlers.entry(event.to_string()).or_default().push(Box::new(handler));
    }

    pub fn emit(&self, event: &str, payload: &str) -> Vec<String> {
        match self.handlers.get(event) {
            Some(handlers) => handlers.iter().map(|h| h(payload)).collect(),
            None => Vec::new(),
        }
    }

    pub fn handler_count(&self, event: &str) -> usize {
        self.handlers.get(event).map_or(0, Vec::len)
    }
}

pub fn make_counter() -> impl FnMut() -> u32 {
    let mut count = 0;
    move || {
        count += 1;
        count
    }
}

pub fn apply_twice<F: FnMut(i32) -> i32>(mut f: F, x: i32) -> i32 {
    let y = f(x);
    f(y)
}

pub fn run_once<F: FnOnce() -> String>(f: F) -> String {
    f()
}

pub fn compose<F, G>(f: F, g: G) -> impl Fn(i32) -> i32
where
    F: Fn(i32) -> i32,
    G: Fn(i32) -> i32,
{
    move |x| g(f(x))
}
