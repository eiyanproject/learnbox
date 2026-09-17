use std::collections::HashMap;
use std::io::{self, BufRead, BufReader, Write};
use std::net::{Shutdown, TcpListener, TcpStream};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::mpsc::{Sender, channel};
use std::sync::{Arc, Mutex, RwLock};
use std::thread::{self, JoinHandle};

pub type Store = Arc<RwLock<HashMap<String, String>>>;

type Job = Box<dyn FnOnce() + Send + 'static>;

struct Pool {
    sender: Option<Sender<Job>>,
    workers: Vec<JoinHandle<()>>,
}

impl Pool {
    fn new(size: usize) -> Self {
        let (sender, receiver) = channel::<Job>();
        let receiver = Arc::new(Mutex::new(receiver));
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
        Pool { sender: Some(sender), workers }
    }

    fn execute<F: FnOnce() + Send + 'static>(&self, job: F) {
        if let Some(sender) = &self.sender {
            let _ = sender.send(Box::new(job));
        }
    }

    fn shutdown(&mut self) {
        self.sender = None; // dropping every sender ends the workers' recv
        for worker in self.workers.drain(..) {
            let _ = worker.join();
        }
    }
}

pub struct Server {
    store: Store,
    running: Arc<AtomicBool>,
    accept: Option<JoinHandle<()>>,
    pool: Arc<Mutex<Option<Pool>>>,
    /// Open connections by id, so shutdown can close them; otherwise a worker
    /// blocked in read_line would keep the pool alive forever. Each handler
    /// removes its own entry when the connection ends.
    clients: Arc<Mutex<HashMap<u64, TcpStream>>>,
    next_client_id: Arc<AtomicU64>,
    port: u16,
}

impl Server {
    pub fn new() -> Self {
        Server {
            store: Arc::new(RwLock::new(HashMap::new())),
            running: Arc::new(AtomicBool::new(false)),
            accept: None,
            pool: Arc::new(Mutex::new(None)),
            clients: Arc::new(Mutex::new(HashMap::new())),
            next_client_id: Arc::new(AtomicU64::new(0)),
            port: 0,
        }
    }

    pub fn start(&mut self, host: &str, port: u16) -> io::Result<u16> {
        let listener = TcpListener::bind((host, port))?;
        let bound = listener.local_addr()?.port();
        self.port = bound;
        self.running.store(true, Ordering::SeqCst);
        *self.pool.lock().unwrap() = Some(Pool::new(16));

        let store = Arc::clone(&self.store);
        let running = Arc::clone(&self.running);
        let pool = Arc::clone(&self.pool);
        let clients = Arc::clone(&self.clients);
        let ids = Arc::clone(&self.next_client_id);
        self.accept = Some(thread::spawn(move || {
            for stream in listener.incoming() {
                if !running.load(Ordering::SeqCst) {
                    break;
                }
                let Ok(stream) = stream else { continue };
                let id = ids.fetch_add(1, Ordering::SeqCst);
                if let Ok(handle) = stream.try_clone() {
                    clients.lock().unwrap().insert(id, handle);
                }
                let store = Arc::clone(&store);
                let clients = Arc::clone(&clients);
                if let Some(pool) = pool.lock().unwrap().as_ref() {
                    pool.execute(move || {
                        if let Err(e) = handle_client(&store, &stream) {
                            eprintln!("connection ended: {e}");
                        }
                        // Close it and stop tracking it, so a client waiting
                        // for EOF sees the connection go away.
                        let _ = stream.shutdown(Shutdown::Both);
                        clients.lock().unwrap().remove(&id);
                    });
                }
            }
        }));
        Ok(bound)
    }

    pub fn stop(&mut self) {
        if !self.running.swap(false, Ordering::SeqCst) {
            return;
        }
        // Wake the blocking accept() by connecting to ourselves once.
        let _ = TcpStream::connect(("127.0.0.1", self.port));
        if let Some(accept) = self.accept.take() {
            let _ = accept.join();
        }
        // Close every open connection so the workers stop waiting for input.
        for (_, client) in self.clients.lock().unwrap().drain() {
            let _ = client.shutdown(Shutdown::Both);
        }
        if let Some(mut pool) = self.pool.lock().unwrap().take() {
            pool.shutdown();
        }
    }

    pub fn store_len(&self) -> usize {
        self.store.read().unwrap().len()
    }
}

impl Drop for Server {
    fn drop(&mut self) {
        self.stop();
    }
}

fn handle_client(store: &Store, stream: &TcpStream) -> io::Result<()> {
    let mut writer = stream.try_clone()?;
    let mut reader = BufReader::new(stream.try_clone()?);
    let mut line = String::new();
    loop {
        line.clear();
        if reader.read_line(&mut line)? == 0 {
            return Ok(());
        }
        let (reply, close) = execute(store, line.trim_end());
        writeln!(writer, "{reply}")?;
        writer.flush()?;
        if close {
            return Ok(());
        }
    }
}

/// Runs one command against the store and returns (reply, should_close).
pub fn execute(store: &Store, line: &str) -> (String, bool) {
    let mut parts = line.trim().splitn(3, ' ');
    let command = parts.next().unwrap_or("").to_uppercase();
    let args: Vec<&str> = parts.collect();
    match (command.as_str(), args.as_slice()) {
        ("SET", [key, value]) => {
            store.write().unwrap().insert((*key).to_string(), (*value).to_string());
            ("OK".to_string(), false)
        }
        ("GET", [key]) => {
            let found = store.read().unwrap().get(*key).cloned();
            (found.unwrap_or_else(|| "NIL".to_string()), false)
        }
        ("DEL", [key]) => {
            let existed = store.write().unwrap().remove(*key).is_some();
            (if existed { "1" } else { "0" }.to_string(), false)
        }
        ("KEYS", []) => {
            let map = store.read().unwrap();
            let mut keys: Vec<&str> = map.keys().map(String::as_str).collect();
            keys.sort();
            (keys.join(" "), false)
        }
        ("PING", []) => ("PONG".to_string(), false),
        ("QUIT", []) => ("BYE".to_string(), true),
        _ => ("ERR unknown command".to_string(), false),
    }
}
