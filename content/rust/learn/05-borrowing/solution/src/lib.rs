pub fn first_word(s: &str) -> &str {
    for (i, ch) in s.char_indices() {
        if ch == ' ' {
            return &s[..i];
        }
    }
    s
}

pub fn sum(nums: &[i32]) -> i32 {
    let mut total = 0;
    for n in nums {
        total += *n;
    }
    total
}

pub fn double_all(nums: &mut [i32]) {
    for n in nums.iter_mut() {
        *n *= 2;
    }
}

pub fn append_greeting(buf: &mut String, name: &str) {
    buf.push_str("Hello, ");
    buf.push_str(name);
    buf.push('\n');
}
