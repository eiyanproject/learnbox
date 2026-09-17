use std::collections::HashMap;
use std::io::{self, BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex, RwLock};
use std::thread::{self, JoinHandle};

pub type Store = Arc<RwLock<HashMap<String, String>>>;

pub struct Server {
    store: Store,
    // shutdown flag, accept thread, worker pool
}

impl Server {
    pub fn new() -> Self {
        todo!()
    }

    /// Binds and starts accepting. Returns the port actually bound.
    pub fn start(&mut self, host: &str, port: u16) -> io::Result<u16> {
        todo!()
    }

    pub fn stop(&mut self) {
        todo!()
    }

    pub fn store_len(&self) -> usize {
        self.store.read().unwrap().len()
    }
}

/// Runs one command against the store and returns (reply, should_close).
pub fn execute(store: &Store, line: &str) -> (String, bool) {
    todo!()
}
