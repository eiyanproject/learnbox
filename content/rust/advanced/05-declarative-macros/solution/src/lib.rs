#[macro_export]
macro_rules! hashmap {
    ($($key:expr => $value:expr),* $(,)?) => {{
        #[allow(unused_mut)]
        let mut map = ::std::collections::HashMap::new();
        $( map.insert($key, $value); )*
        map
    }};
}

#[macro_export]
macro_rules! max_of {
    ($x:expr $(,)?) => {
        $x
    };
    ($x:expr, $($rest:expr),+ $(,)?) => {{
        let a = $x;
        let b = $crate::max_of!($($rest),+);
        if a > b { a } else { b }
    }};
}

#[macro_export]
macro_rules! count {
    () => {
        0usize
    };
    ($head:tt $($tail:tt)*) => {
        1usize + $crate::count!($($tail)*)
    };
}

#[macro_export]
macro_rules! newtype {
    ($name:ident, $inner:ty) => {
        #[derive(Debug, Clone, Copy, PartialEq)]
        pub struct $name(pub $inner);

        impl From<$inner> for $name {
            fn from(value: $inner) -> Self {
                $name(value)
            }
        }
    };
}
