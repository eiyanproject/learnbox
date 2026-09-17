pub fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    todo!()
}

/// # Safety
/// Document the contract, then implement it with raw pointers.
pub unsafe fn swap_unchecked(slice: &mut [i32], a: usize, b: usize) {
    todo!()
}

pub struct Buffer {
    bytes: Vec<u8>,
}

impl Buffer {
    pub fn new() -> Self {
        Buffer { bytes: Vec::new() }
    }

    // push, len, capacity, as_bytes, as_str, as_str_unchecked
}
