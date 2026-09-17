use std::fs::{File, OpenOptions};
use std::io::{self, BufRead, BufReader, BufWriter, Read, Write};
use std::path::Path;

pub fn count_lines_and_words<R: BufRead>(reader: R) -> io::Result<(usize, usize)> {
    todo!()
}

pub fn write_report<W: Write>(out: W, rows: &[(&str, u32)]) -> io::Result<()> {
    todo!()
}

pub fn sum_column(path: impl AsRef<Path>, column: usize) -> io::Result<f64> {
    todo!()
}

pub fn append_log(path: impl AsRef<Path>, line: &str) -> io::Result<()> {
    todo!()
}

pub fn copy_upper(src: impl AsRef<Path>, dst: impl AsRef<Path>) -> io::Result<usize> {
    todo!()
}
