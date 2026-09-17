// `longest` does not compile yet: it needs a lifetime parameter.
pub fn longest(a: &str, b: &str) -> &str {
    todo!()
}

pub struct Stack<T> {
    items: Vec<T>,
}

impl<T> Stack<T> {
    pub fn new() -> Self {
        todo!()
    }

    pub fn push(&mut self, item: T) {
        todo!()
    }

    pub fn pop(&mut self) -> Option<T> {
        todo!()
    }

    pub fn peek(&self) -> Option<&T> {
        todo!()
    }

    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn is_empty(&self) -> bool {
        todo!()
    }
}

pub struct Excerpt<'a> {
    pub text: &'a str,
}

impl<'a> Excerpt<'a> {
    pub fn first_sentence(&self) -> &'a str {
        todo!()
    }
}
