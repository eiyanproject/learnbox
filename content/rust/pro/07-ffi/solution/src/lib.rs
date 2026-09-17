use std::ffi::{CStr, CString, c_char, c_int};

unsafe extern "C" {
    fn strlen(s: *const c_char) -> usize;
    fn abs(n: c_int) -> c_int;
}

pub fn c_strlen(s: &str) -> Option<usize> {
    let owned = CString::new(s).ok()?;
    // SOUND: `owned` is a valid NUL-terminated C string and outlives the call.
    Some(unsafe { strlen(owned.as_ptr()) })
}

pub fn c_abs(n: i32) -> i32 {
    // SOUND: abs has no preconditions beyond its argument type.
    unsafe { abs(n as c_int) as i32 }
}

/// # Safety
/// `ptr` must be a valid, NUL-terminated C string that stays alive for the call.
pub unsafe fn from_c_string(ptr: *const c_char) -> String {
    if ptr.is_null() {
        return String::new();
    }
    // SOUND: the caller promises a valid NUL-terminated string.
    unsafe { CStr::from_ptr(ptr).to_string_lossy().into_owned() }
}

#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Point {
    pub x: f64,
    pub y: f64,
}

#[unsafe(no_mangle)]
pub extern "C" fn learnbox_distance(a: Point, b: Point) -> f64 {
    ((a.x - b.x).powi(2) + (a.y - b.y).powi(2)).sqrt()
}

/// Sums `len` `i32`s starting at `ptr`.
///
/// # Safety
/// `ptr` must point at `len` initialised `i32`s, or be null.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn learnbox_sum(ptr: *const i32, len: usize) -> i64 {
    if ptr.is_null() || len == 0 {
        return 0;
    }
    // Never let a panic unwind into C.
    std::panic::catch_unwind(|| {
        // SOUND: the caller promises `len` initialised values at `ptr`.
        let values = unsafe { std::slice::from_raw_parts(ptr, len) };
        values.iter().map(|&x| x as i64).sum()
    })
    .unwrap_or(0)
}
