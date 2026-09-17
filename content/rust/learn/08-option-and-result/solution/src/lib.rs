use std::num::ParseIntError;

pub fn find_index(items: &[&str], target: &str) -> Option<usize> {
    for (i, item) in items.iter().enumerate() {
        if *item == target {
            return Some(i);
        }
    }
    None
}

pub fn parse_age(s: &str) -> Result<u8, String> {
    let n: i64 = s.trim().parse().map_err(|_| format!("not a number: {s}"))?;
    if !(0..=150).contains(&n) {
        return Err(format!("out of range: {n}"));
    }
    Ok(n as u8)
}

pub fn add_strings(a: &str, b: &str) -> Result<i64, ParseIntError> {
    Ok(a.trim().parse::<i64>()? + b.trim().parse::<i64>()?)
}

pub fn safe_divide(a: i32, b: i32) -> Option<i32> {
    a.checked_div(b)
}
