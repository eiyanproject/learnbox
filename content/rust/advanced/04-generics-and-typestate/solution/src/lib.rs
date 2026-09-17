use std::marker::PhantomData;

pub trait Shape {
    const SIDES: u32;
    fn name() -> &'static str;
}

pub struct Triangle;
pub struct Square;

impl Shape for Triangle {
    const SIDES: u32 = 3;
    fn name() -> &'static str {
        "triangle"
    }
}

impl Shape for Square {
    const SIDES: u32 = 4;
    fn name() -> &'static str {
        "square"
    }
}

pub fn total_sides<A: Shape, B: Shape>() -> u32 {
    A::SIDES + B::SIDES
}

pub struct Height;
pub struct Width;

pub struct Meters<T> {
    value: f64,
    _tag: PhantomData<T>,
}

impl<T> Meters<T> {
    pub fn new(value: f64) -> Self {
        Meters { value, _tag: PhantomData }
    }

    pub fn value(&self) -> f64 {
        self.value
    }
}

pub fn area(h: Meters<Height>, w: Meters<Width>) -> f64 {
    h.value * w.value
}

pub struct Empty;
pub struct HasUrl;

pub struct Request<State> {
    url: String,
    headers: Vec<(String, String)>,
    _state: PhantomData<State>,
}

impl Request<Empty> {
    pub fn new() -> Self {
        Request { url: String::new(), headers: Vec::new(), _state: PhantomData }
    }

    pub fn url(self, url: &str) -> Request<HasUrl> {
        Request { url: url.to_string(), headers: self.headers, _state: PhantomData }
    }
}

impl Request<HasUrl> {
    pub fn header(mut self, key: &str, value: &str) -> Self {
        self.headers.push((key.to_string(), value.to_string()));
        self
    }

    pub fn send(&self) -> String {
        let headers: Vec<String> = self.headers.iter().map(|(k, v)| format!("{k}: {v}")).collect();
        format!("GET {} [{}]", self.url, headers.join(", "))
    }
}

pub fn largest_by<T, K, F>(items: &[T], key: F) -> Option<&T>
where
    F: Fn(&T) -> K,
    K: PartialOrd,
{
    let mut iter = items.iter();
    let mut best = iter.next()?;
    let mut best_key = key(best);
    for item in iter {
        let k = key(item);
        if k > best_key {
            best = item;
            best_key = k;
        }
    }
    Some(best)
}
