/// Returns the text with "!" added to the end.
pub fn exclaim(mut s: String) -> String {
    s.push('!');
    s
}

/// Returns a copy of the first name and how many names there are.
pub fn first_and_count(names: Vec<String>) -> (String, usize) {
    let first = names[0].clone();
    (first, names.len())
}

/// Returns two separate copies of the text.
pub fn twice(s: String) -> (String, String) {
    let a = s.clone();
    let b = s;
    (a, b)
}

/// Returns every word upper-cased, and logs how many there were.
pub fn shout_all(words: Vec<String>) -> Vec<String> {
    let mut out = Vec::new();
    for w in &words {
        out.push(w.to_uppercase());
    }
    println!("shouted {} words", words.len());
    out
}
