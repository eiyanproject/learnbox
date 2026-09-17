use std::sync::mpsc::{self, Receiver, Sender};
use std::sync::{Arc, Mutex};
use std::thread::{self, JoinHandle};

pub fn collect_from_producers(producers: usize, per_producer: usize) -> Vec<String> {
    let (tx, rx) = mpsc::channel();
    for id in 0..producers {
        let tx = tx.clone();
        thread::spawn(move || {
            for n in 0..per_producer {
                tx.send(format!("p{id}-{n}")).unwrap();
            }
        });
    }
    drop(tx);
    let mut all: Vec<String> = rx.into_iter().collect();
    all.sort();
    all
}

pub type Job = Box<dyn FnOnce() + Send + 'static>;

pub struct WorkerPool {
    sender: Sender<Job>,
    workers: Vec<JoinHandle<()>>,
}

impl WorkerPool {
    pub fn new(size: usize) -> Self {
        assert!(size >= 1, "a pool needs at least one worker");
        let (sender, receiver) = mpsc::channel::<Job>();
        let receiver: Arc<Mutex<Receiver<Job>>> = Arc::new(Mutex::new(receiver));
        let workers = (0..size)
            .map(|_| {
                let receiver = Arc::clone(&receiver);
                thread::spawn(move || {
                    loop {
                        let job = receiver.lock().unwrap().recv();
                        match job {
                            Ok(job) => job(),
                            Err(_) => break,
                        }
                    }
                })
            })
            .collect();
        WorkerPool { sender, workers }
    }

    pub fn execute<F: FnOnce() + Send + 'static>(&self, job: F) {
        self.sender.send(Box::new(job)).expect("workers are gone");
    }

    pub fn shutdown(self) {
        drop(self.sender);
        for worker in self.workers {
            worker.join().unwrap();
        }
    }
}

pub fn pipeline(n: u64) -> Vec<u64> {
    let (numbers_tx, numbers_rx) = mpsc::channel();
    let (squares_tx, squares_rx) = mpsc::channel();

    let source = thread::spawn(move || {
        for i in 1..=n {
            numbers_tx.send(i).unwrap();
        }
    });
    let square = thread::spawn(move || {
        for i in numbers_rx {
            squares_tx.send(i * i).unwrap();
        }
    });

    let out: Vec<u64> = squares_rx.into_iter().collect();
    source.join().unwrap();
    square.join().unwrap();
    out
}
