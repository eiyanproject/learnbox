use std::ffi::{CStr, CString, c_char, c_int};

// Declare the C functions you call here.

pub fn c_strlen(s: &str) -> Option<usize> {
    todo!()
}

pub fn c_abs(n: i32) -> i32 {
    todo!()
}

/// # Safety
/// `ptr` must be a valid, NUL-terminated C string.
pub unsafe fn from_c_string(ptr: *const c_char) -> String {
    todo!()
}

// #[repr(C)] pub struct Point { pub x: f64, pub y: f64 }

// pub extern "C" fn learnbox_distance(a: Point, b: Point) -> f64

// pub extern "C" fn learnbox_sum(ptr: *const i32, len: usize) -> i64
