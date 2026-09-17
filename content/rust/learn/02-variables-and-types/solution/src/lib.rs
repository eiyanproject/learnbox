pub fn celsius_to_fahrenheit(c: f64) -> f64 {
    c * 9.0 / 5.0 + 32.0
}

/// (hours, minutes, seconds)
pub fn seconds_to_hms(total: u32) -> (u32, u32, u32) {
    (total / 3600, (total % 3600) / 60, total % 60)
}

pub fn average(a: i32, b: i32) -> f64 {
    (a as f64 + b as f64) / 2.0
}

pub fn sum_array(values: [i64; 5]) -> i64 {
    let mut total = 0;
    for n in values {
        total += n;
    }
    total
}
