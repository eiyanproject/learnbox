use std::future::Future;
use std::pin::Pin;
use std::sync::Arc;
use std::task::{Context, Poll, Wake, Waker};
use std::thread;
use std::time::{Duration, Instant};

pub struct Ready<T>(Option<T>);

pub fn ready<T>(value: T) -> Ready<T> {
    Ready(Some(value))
}

// impl<T> Future for Ready<T>

pub struct Delay {
    deadline: Instant,
    started: bool,
}

pub fn delay(duration: Duration) -> Delay {
    Delay { deadline: Instant::now() + duration, started: false }
}

// impl Future for Delay

pub struct Counter {
    remaining: usize,
    polls: usize,
}

pub fn counter(n: usize) -> Counter {
    Counter { remaining: n, polls: 0 }
}

// impl Future for Counter

pub fn block_on<F: Future>(future: F) -> F::Output {
    todo!()
}
