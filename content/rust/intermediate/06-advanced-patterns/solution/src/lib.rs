pub fn describe_slice(items: &[&str]) -> String {
    match items {
        [] => "nothing".to_string(),
        [only] => format!("only {only}"),
        [first, .., last] => format!("{first} to {last} ({} items)", items.len()),
    }
}

pub fn classify_age(age: u32) -> String {
    match age {
        0 => "newborn".to_string(),
        1..=12 => "child".to_string(),
        teen @ 13..=19 => format!("teenager aged {teen}"),
        _ => "adult".to_string(),
    }
}

pub fn parse_kv(line: &str) -> Option<(&str, &str)> {
    let Some((key, value)) = line.split_once('=') else {
        return None;
    };
    let key = key.trim();
    if key.is_empty() {
        return None;
    }
    Some((key, value.trim()))
}

pub fn sum_pairs(values: &[i32]) -> Vec<i32> {
    match values {
        [] => vec![],
        [last] => vec![*last],
        [a, b, rest @ ..] => {
            let mut out = vec![a + b];
            out.extend(sum_pairs(rest));
            out
        }
    }
}

pub enum Destination {
    Domestic { express: bool },
    International { country: String },
}

pub struct Order {
    pub id: u32,
    pub items: Vec<String>,
    pub destination: Destination,
}

pub fn total_shipping(orders: &[Order]) -> u32 {
    orders
        .iter()
        .map(|order| match order {
            Order { items, .. } if items.is_empty() => 0,
            Order { destination: Destination::Domestic { express: true }, .. } => 15,
            Order { destination: Destination::Domestic { .. }, .. } => 5,
            Order { destination: Destination::International { country }, .. } if country == "SG" => 20,
            Order { destination: Destination::International { .. }, .. } => 30,
        })
        .sum()
}
