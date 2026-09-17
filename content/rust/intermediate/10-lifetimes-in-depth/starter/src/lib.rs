pub struct Tokenizer<'a> {
    input: &'a str,
    pos: usize,
}

impl<'a> Tokenizer<'a> {
    pub fn new(input: &'a str) -> Self {
        Tokenizer { input, pos: 0 }
    }
}

// impl<'a> Iterator for Tokenizer<'a> { ... }

pub fn longest_line(text: &str) -> &str {
    todo!()
}

// This signature ties the result to both inputs. Loosen it.
pub fn pick_first<'a>(a: &'a str, _b: &'a str) -> &'a str {
    a
}

pub struct Registry {
    names: Vec<&'static str>,
}

impl Registry {
    pub fn new() -> Self {
        Registry { names: Vec::new() }
    }

    // register, names
}
