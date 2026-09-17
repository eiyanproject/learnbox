use std::ffi::CString;

use ffi_lesson::*;

#[test]
fn strlen_through_c() {
    assert_eq!(c_strlen("hello"), Some(5));
    assert_eq!(c_strlen(""), Some(0));
    assert_eq!(c_strlen("héllo"), Some(6), "strlen counts bytes");
}

#[test]
fn interior_nul_is_rejected() {
    assert_eq!(c_strlen("bad\0string"), None);
}

#[test]
fn abs_through_c() {
    assert_eq!(c_abs(-7), 7);
    assert_eq!(c_abs(7), 7);
    assert_eq!(c_abs(0), 0);
}

#[test]
fn reads_a_c_string() {
    let owned = CString::new("from C").unwrap();
    let text = unsafe { from_c_string(owned.as_ptr()) };
    assert_eq!(text, "from C");
    assert_eq!(unsafe { from_c_string(std::ptr::null()) }, "");
}

#[test]
fn invalid_utf8_is_replaced_not_rejected() {
    let bytes = CString::new(vec![0x68u8, 0x69, 0xff]).unwrap();
    let text = unsafe { from_c_string(bytes.as_ptr()) };
    assert!(text.starts_with("hi"));
    assert!(text.contains('\u{fffd}'));
}

#[test]
fn repr_c_struct_and_distance() {
    assert_eq!(std::mem::size_of::<Point>(), 16);
    let d = learnbox_distance(Point { x: 0.0, y: 0.0 }, Point { x: 3.0, y: 4.0 });
    assert!((d - 5.0).abs() < 1e-12);
}

#[test]
fn sum_from_a_raw_array() {
    let values: Vec<i32> = (1..=100).collect();
    let total = unsafe { learnbox_sum(values.as_ptr(), values.len()) };
    assert_eq!(total, 5050);
    assert_eq!(unsafe { learnbox_sum(std::ptr::null(), 10) }, 0);
    assert_eq!(unsafe { learnbox_sum(values.as_ptr(), 0) }, 0);
}

#[test]
fn sum_does_not_overflow_i32() {
    let values = vec![i32::MAX, i32::MAX, i32::MAX];
    assert_eq!(unsafe { learnbox_sum(values.as_ptr(), 3) }, 3 * i32::MAX as i64);
}

#[test]
fn exported_symbols_keep_their_names() {
    let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/src/lib.rs")).unwrap();
    assert!(src.contains("no_mangle"), "C cannot find a mangled symbol");
    assert!(src.contains("catch_unwind"), "a panic must not unwind into C");
}
