use std::any::Any;

pub trait Plugin {
    fn name(&self) -> &str;
    fn run(&mut self, input: &str) -> String;
    fn as_any(&self) -> &dyn Any;
}

pub struct Uppercase;

impl Plugin for Uppercase {
    fn name(&self) -> &str {
        "upper"
    }
    fn run(&mut self, input: &str) -> String {
        input.to_uppercase()
    }
    fn as_any(&self) -> &dyn Any {
        self
    }
}

pub struct Counter {
    pub calls: usize,
}

impl Plugin for Counter {
    fn name(&self) -> &str {
        "counter"
    }
    fn run(&mut self, input: &str) -> String {
        self.calls += 1;
        input.to_string()
    }
    fn as_any(&self) -> &dyn Any {
        self
    }
}

pub struct Suffix(pub String);

impl Plugin for Suffix {
    fn name(&self) -> &str {
        "suffix"
    }
    fn run(&mut self, input: &str) -> String {
        format!("{input}{}", self.0)
    }
    fn as_any(&self) -> &dyn Any {
        self
    }
}

pub struct Registry {
    plugins: Vec<Box<dyn Plugin>>,
}

impl Registry {
    pub fn new() -> Self {
        Registry { plugins: Vec::new() }
    }

    pub fn register(&mut self, plugin: Box<dyn Plugin>) {
        self.plugins.push(plugin);
    }

    pub fn names(&self) -> Vec<&str> {
        self.plugins.iter().map(|p| p.name()).collect()
    }

    pub fn run_all(&mut self, input: &str) -> String {
        let mut text = input.to_string();
        for plugin in self.plugins.iter_mut() {
            text = plugin.run(&text);
        }
        text
    }

    pub fn find<T: Plugin + 'static>(&self) -> Option<&T> {
        self.plugins.iter().find_map(|p| p.as_any().downcast_ref::<T>())
    }
}

pub fn describe_value(value: &dyn Any) -> String {
    if let Some(n) = value.downcast_ref::<i32>() {
        format!("i32 {n}")
    } else if let Some(s) = value.downcast_ref::<String>() {
        format!("String {s}")
    } else if let Some(s) = value.downcast_ref::<&str>() {
        format!("&str {s}")
    } else {
        "something else".to_string()
    }
}
