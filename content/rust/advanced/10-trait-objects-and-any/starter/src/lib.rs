use std::any::Any;

pub trait Plugin {
    fn name(&self) -> &str;
    // run, as_any
}

pub struct Uppercase;

pub struct Counter {
    pub calls: usize,
}

pub struct Suffix(pub String);

pub struct Registry {
    plugins: Vec<Box<dyn Plugin>>,
}

impl Registry {
    pub fn new() -> Self {
        Registry { plugins: Vec::new() }
    }

    // register, names, run_all, find
}

pub fn describe_value(value: &dyn Any) -> String {
    todo!()
}
