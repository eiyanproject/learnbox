use std::fs::{File, OpenOptions};
use std::io::{self, BufRead, BufReader, BufWriter, Read, Write};
use std::path::Path;

pub fn count_lines_and_words<R: BufRead>(reader: R) -> io::Result<(usize, usize)> {
    let mut lines = 0;
    let mut words = 0;
    for line in reader.lines() {
        let line = line?;
        lines += 1;
        words += line.split_whitespace().count();
    }
    Ok((lines, words))
}

pub fn write_report<W: Write>(mut out: W, rows: &[(&str, u32)]) -> io::Result<()> {
    for (name, value) in rows {
        writeln!(out, "{name:<10}{value:>5}")?;
    }
    out.flush()
}

pub fn sum_column(path: impl AsRef<Path>, column: usize) -> io::Result<f64> {
    let reader = BufReader::new(File::open(path)?);
    let mut total = 0.0;
    for (i, line) in reader.lines().enumerate().skip(1) {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        let field = line.split(',').nth(column).unwrap_or("").trim();
        let value: f64 = field
            .parse()
            .map_err(|_| io::Error::new(io::ErrorKind::InvalidData, format!("line {}: not a number: {field:?}", i + 1)))?;
        total += value;
    }
    Ok(total)
}

pub fn append_log(path: impl AsRef<Path>, line: &str) -> io::Result<()> {
    let mut file = OpenOptions::new().create(true).append(true).open(path)?;
    writeln!(file, "{line}")
}

pub fn copy_upper(src: impl AsRef<Path>, dst: impl AsRef<Path>) -> io::Result<usize> {
    let mut reader = BufReader::new(File::open(src)?);
    let mut writer = BufWriter::new(File::create(dst)?);
    let mut buf = [0u8; 8192];
    let mut written = 0;
    loop {
        let n = reader.read(&mut buf)?;
        if n == 0 {
            break;
        }
        buf[..n].make_ascii_uppercase();
        writer.write_all(&buf[..n])?;
        written += n;
    }
    writer.flush()?;
    Ok(written)
}
