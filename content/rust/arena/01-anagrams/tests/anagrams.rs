use arena_anagrams::*;

fn strings(groups: &[&[&str]]) -> Vec<Vec<String>> {
    groups.iter().map(|g| g.iter().map(|w| w.to_string()).collect()).collect()
}

#[test]
fn plain_anagrams() {
    assert!(are_anagrams("listen", "silent"));
    assert!(are_anagrams("a", "a"));
}

#[test]
fn not_anagrams() {
    assert!(!are_anagrams("listen", "silence"));
    assert!(!are_anagrams("abc", "abd"));
}

#[test]
fn letter_counts_matter() {
    assert!(!are_anagrams("aab", "abb"));
    assert!(!are_anagrams("aa", "a"));
}

#[test]
fn case_does_not_matter() {
    assert!(are_anagrams("Listen", "SILENT"));
}

#[test]
fn only_letters_count() {
    assert!(are_anagrams("Dormitory", "dirty room"));
    assert!(are_anagrams("a gentleman", "Elegant Man!"));
    assert!(are_anagrams("r2d2", "dr"));
}

#[test]
fn nothing_is_an_anagram_of_nothing() {
    assert!(are_anagrams("", ""));
    assert!(are_anagrams("", " !? "));
    assert!(!are_anagrams("", "a"));
}

#[test]
fn groups_the_example() {
    assert_eq!(
        group_anagrams(&["eat", "tea", "tan", "ate", "nat", "bat"]),
        strings(&[&["eat", "tea", "ate"], &["tan", "nat"], &["bat"]])
    );
}

#[test]
fn groups_keep_spelling_and_order() {
    assert_eq!(group_anagrams(&["Tea", "bat", "EAT", "Tab"]), strings(&[&["Tea", "EAT"], &["bat", "Tab"]]));
}

#[test]
fn a_repeated_word_stays_repeated() {
    assert_eq!(group_anagrams(&["on", "no", "on"]), strings(&[&["on", "no", "on"]]));
}

#[test]
fn no_words_no_groups() {
    assert!(group_anagrams(&[]).is_empty());
}

#[test]
fn every_word_alone() {
    assert_eq!(group_anagrams(&["one", "two", "six"]), strings(&[&["one"], &["two"], &["six"]]));
}
