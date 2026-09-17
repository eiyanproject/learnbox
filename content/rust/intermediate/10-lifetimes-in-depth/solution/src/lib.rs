pub struct Tokenizer<'a> {
    input: &'a str,
    pos: usize,
}

impl<'a> Tokenizer<'a> {
    pub fn new(input: &'a str) -> Self {
        Tokenizer { input, pos: 0 }
    }
}

impl<'a> Iterator for Tokenizer<'a> {
    type Item = &'a str;

    fn next(&mut self) -> Option<&'a str> {
        let rest = &self.input[self.pos..];
        let start = self.pos + rest.char_indices().find(|(_, c)| !c.is_whitespace())?.0;
        let token_rest = &self.input[start..];
        let end = start
            + token_rest
                .char_indices()
                .find(|(_, c)| c.is_whitespace())
                .map_or(token_rest.len(), |(i, _)| i);
        self.pos = end;
        Some(&self.input[start..end])
    }
}

pub fn longest_line(text: &str) -> &str {
    let mut best = "";
    for line in text.lines() {
        if line.len() > best.len() {
            best = line;
        }
    }
    best
}

pub fn pick_first<'a, 'b>(a: &'a str, _b: &'b str) -> &'a str {
    a
}

pub struct Registry {
    names: Vec<&'static str>,
}

impl Registry {
    pub fn new() -> Self {
        Registry { names: Vec::new() }
    }

    pub fn register(&mut self, name: &'static str) {
        self.names.push(name);
    }

    pub fn names(&self) -> Vec<&'static str> {
        let mut v = self.names.clone();
        v.sort();
        v
    }
}
