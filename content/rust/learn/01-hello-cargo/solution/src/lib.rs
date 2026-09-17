/// "Hello, <name>!"
pub fn greeting(name: &str) -> String {
    format!("Hello, {name}!")
}

/// The title between two lines of '=' the same length as the title.
pub fn banner(title: &str) -> String {
    let line = "=".repeat(title.len());
    format!("{line}\n{title}\n{line}")
}
