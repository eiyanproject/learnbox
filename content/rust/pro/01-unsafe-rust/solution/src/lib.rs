use std::slice;

pub fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();
    assert!(mid <= len, "mid {mid} is past the end ({len})");
    // SOUND: mid <= len was checked, so both ranges are inside one allocation,
    // and they do not overlap, so handing out two &mut is not aliasing.
    unsafe { (slice::from_raw_parts_mut(ptr, mid), slice::from_raw_parts_mut(ptr.add(mid), len - mid)) }
}

/// Swaps two elements without bounds checks.
///
/// # Safety
/// `a` and `b` must both be less than `slice.len()`.
pub unsafe fn swap_unchecked(slice: &mut [i32], a: usize, b: usize) {
    let ptr = slice.as_mut_ptr();
    // SOUND: the caller promises both indices are in bounds, so both pointers
    // are inside the allocation; ptr::swap handles a == b.
    unsafe { std::ptr::swap(ptr.add(a), ptr.add(b)) }
}

pub struct Buffer {
    bytes: Vec<u8>,
}

impl Buffer {
    pub fn new() -> Self {
        Buffer { bytes: Vec::with_capacity(0) }
    }

    pub fn push(&mut self, byte: u8) {
        if self.bytes.len() == self.bytes.capacity() {
            let extra = self.bytes.capacity().max(8);
            self.bytes.reserve_exact(extra);
        }
        self.bytes.push(byte);
    }

    pub fn len(&self) -> usize {
        self.bytes.len()
    }

    pub fn is_empty(&self) -> bool {
        self.bytes.is_empty()
    }

    pub fn capacity(&self) -> usize {
        self.bytes.capacity()
    }

    pub fn as_bytes(&self) -> &[u8] {
        &self.bytes
    }

    pub fn as_str(&self) -> Option<&str> {
        std::str::from_utf8(&self.bytes).ok()
    }

    /// # Safety
    /// The buffer must contain valid UTF-8.
    pub unsafe fn as_str_unchecked(&self) -> &str {
        // SOUND: the caller promises the bytes are valid UTF-8, which is the
        // only invariant `str` has beyond `[u8]`.
        unsafe { std::str::from_utf8_unchecked(&self.bytes) }
    }
}

impl Extend<u8> for Buffer {
    fn extend<I: IntoIterator<Item = u8>>(&mut self, iter: I) {
        for byte in iter {
            self.push(byte);
        }
    }
}
