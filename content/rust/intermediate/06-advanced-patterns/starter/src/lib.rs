pub fn describe_slice(items: &[&str]) -> String {
    todo!()
}

pub fn classify_age(age: u32) -> String {
    todo!()
}

pub fn parse_kv(line: &str) -> Option<(&str, &str)> {
    todo!()
}

pub fn sum_pairs(values: &[i32]) -> Vec<i32> {
    todo!()
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
    todo!()
}
