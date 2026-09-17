use std::marker::PhantomData;

pub trait Shape {
    // const SIDES: u32;
    // fn name() -> &'static str;
}

pub struct Triangle;
pub struct Square;

pub struct Height;
pub struct Width;

pub struct Meters<T> {
    value: f64,
    _tag: PhantomData<T>,
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
}

pub fn largest_by<T, K, F>(items: &[T], key: F) -> Option<&T>
where
    F: Fn(&T) -> K,
    K: PartialOrd,
{
    todo!()
}
