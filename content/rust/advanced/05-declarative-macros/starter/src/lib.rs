// Define hashmap!, max_of!, count! and newtype! here, each with #[macro_export].

#[macro_export]
macro_rules! hashmap {
    () => {
        ::std::collections::HashMap::new()
    };
}
