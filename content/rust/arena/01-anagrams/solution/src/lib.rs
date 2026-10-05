/// The letters of a text, lower-cased and sorted: equal for anagrams.
fn key(text: &str) -> Vec<char> {
    let mut letters: Vec<char> = text.chars().filter(|c| c.is_alphabetic()).flat_map(|c| c.to_lowercase()).collect();
    letters.sort_unstable();
    letters
}

pub fn are_anagrams(a: &str, b: &str) -> bool {
    key(a) == key(b)
}

pub fn group_anagrams(words: &[&str]) -> Vec<Vec<String>> {
    let mut groups: Vec<(Vec<char>, Vec<String>)> = Vec::new();
    for word in words {
        let k = key(word);
        match groups.iter_mut().find(|(have, _)| *have == k) {
            Some((_, members)) => members.push(word.to_string()),
            None => groups.push((k, vec![word.to_string()])),
        }
    }
    groups.into_iter().map(|(_, members)| members).collect()
}
