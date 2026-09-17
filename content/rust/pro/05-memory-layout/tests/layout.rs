use std::alloc::{GlobalAlloc, Layout, System};
use std::borrow::Cow;
use std::mem::size_of;
use std::cell::Cell;

use memory_layout::*;

struct Counting;

// Counted per thread, so the numbers hold even when tests run in parallel.
thread_local! {
    static ALLOCATIONS: Cell<usize> = const { Cell::new(0) };
}

fn bump() {
    // try_with: the counter may already be gone during thread teardown.
    let _ = ALLOCATIONS.try_with(|c| c.set(c.get() + 1));
}

unsafe impl GlobalAlloc for Counting {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        bump();
        unsafe { System.alloc(layout) }
    }
    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        unsafe { System.dealloc(ptr, layout) }
    }
    unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, new_size: usize) -> *mut u8 {
        bump();
        unsafe { System.realloc(ptr, layout, new_size) }
    }
}

#[global_allocator]
static ALLOC: Counting = Counting;

fn allocations(f: impl FnOnce()) -> usize {
    let before = ALLOCATIONS.with(|c| c.get());
    f();
    ALLOCATIONS.with(|c| c.get()) - before
}

#[test]
fn field_order_removes_padding() {
    assert_eq!(size_of::<Wasteful>(), 24);
    assert_eq!(size_of::<Packed>(), 16);
}

#[test]
fn packed_still_holds_every_field() {
    let p = Packed::new(1, 2, 3, 4);
    assert_eq!((p.a, p.b, p.c, p.d), (1, 2, 3, 4));
}

#[test]
fn sum_digits_is_correct_and_allocation_free() {
    assert_eq!(sum_digits("a1b2c3"), 6);
    assert_eq!(sum_digits("no digits"), 0);
    assert_eq!(sum_digits("2026-09-18"), 2 + 0 + 2 + 6 + 0 + 9 + 1 + 8);
    let text = "order 66 shipped 1234 units".repeat(20);
    assert_eq!(allocations(|| { std::hint::black_box(sum_digits(&text)); }), 0);
}

#[test]
fn join_allocates_once() {
    assert_eq!(join_with_capacity(&["a", "b", "c"], ", "), "a, b, c");
    assert_eq!(join_with_capacity(&[], "-"), "");
    assert_eq!(join_with_capacity(&["solo"], "-"), "solo");
    let parts: Vec<&str> = "the quick brown fox jumps over the lazy dog".split(' ').collect();
    assert_eq!(allocations(|| { std::hint::black_box(join_with_capacity(&parts, " ")); }), 1);
}

#[test]
fn normalize_borrows_when_possible() {
    assert!(matches!(normalize("already lower"), Cow::Borrowed("already lower")));
    assert!(matches!(normalize("  padded  "), Cow::Borrowed("padded")));
    let upper = normalize("  Mixed Case  ");
    assert!(matches!(upper, Cow::Owned(_)));
    assert_eq!(upper, "mixed case");
    assert_eq!(allocations(|| { std::hint::black_box(normalize("plain text")); }), 0);
}

#[test]
fn buffer_is_reused() {
    let lines = ["one two", "  three  ", "", "four five six"];
    assert_eq!(count_words_reusing_buffer(&lines), [2, 1, 0, 3]);
    let many: Vec<&str> = std::iter::repeat("a b c").take(200).collect();
    let allocs = allocations(|| { std::hint::black_box(count_words_reusing_buffer(&many)); });
    assert!(allocs <= 4, "allocated {allocs} times; reuse one buffer");
}
