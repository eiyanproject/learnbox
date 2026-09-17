use std::sync::mpsc::{self, Receiver, Sender};
use std::sync::{Arc, Mutex};
use std::thread::{self, JoinHandle};

pub fn collect_from_producers(producers: usize, per_producer: usize) -> Vec<String> {
    todo!()
}

pub type Job = Box<dyn FnOnce() + Send + 'static>;

pub struct WorkerPool {
    // sender, workers
}

impl WorkerPool {
    pub fn new(size: usize) -> Self {
        todo!()
    }

    pub fn execute<F: FnOnce() + Send + 'static>(&self, job: F) {
        todo!()
    }

    pub fn shutdown(self) {
        todo!()
    }
}

pub fn pipeline(n: u64) -> Vec<u64> {
    todo!()
}
