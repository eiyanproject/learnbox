use std::future::Future;
use std::pin::Pin;
use std::sync::mpsc::{Receiver, Sender, channel};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};
use std::thread;
use std::time::{Duration, Instant};

pub type BoxFuture = Pin<Box<dyn Future<Output = ()> + Send>>;

pub struct JoinHandle<T> {
    slot: Arc<Mutex<Option<T>>>,
}

impl<T> JoinHandle<T> {
    pub fn take(&self) -> Option<T> {
        self.slot.lock().unwrap().take()
    }
}

struct Task {
    future: Mutex<Option<BoxFuture>>,
    queue: Sender<Arc<Task>>,
}

impl Wake for Task {
    fn wake(self: Arc<Self>) {
        let _ = self.queue.send(self);
    }

    fn wake_by_ref(self: &Arc<Self>) {
        let _ = self.queue.send(Arc::clone(self));
    }
}

pub struct Executor {
    sender: Sender<Arc<Task>>,
    ready: Mutex<Receiver<Arc<Task>>>,
    outstanding: Arc<AtomicUsize>,
}

impl Executor {
    pub fn new() -> Self {
        let (sender, ready) = channel();
        Executor { sender, ready: Mutex::new(ready), outstanding: Arc::new(AtomicUsize::new(0)) }
    }

    pub fn spawn<T, F>(&self, future: F) -> JoinHandle<T>
    where
        F: Future<Output = T> + Send + 'static,
        T: Send + 'static,
    {
        let slot = Arc::new(Mutex::new(None));
        let result = Arc::clone(&slot);
        let wrapped: BoxFuture = Box::pin(async move {
            *result.lock().unwrap() = Some(future.await);
        });
        let task = Arc::new(Task { future: Mutex::new(Some(wrapped)), queue: self.sender.clone() });
        self.outstanding.fetch_add(1, Ordering::SeqCst);
        let _ = self.sender.send(task);
        JoinHandle { slot }
    }

    pub fn run(&self) {
        let ready = self.ready.lock().unwrap();
        while self.outstanding.load(Ordering::SeqCst) > 0 {
            let task = match ready.recv_timeout(Duration::from_millis(50)) {
                Ok(task) => task,
                Err(_) => continue, // every task is parked, waiting for a waker
            };
            let mut slot = task.future.lock().unwrap();
            let Some(mut future) = slot.take() else {
                continue; // already finished; a stale wake
            };
            let waker = Waker::from(Arc::clone(&task));
            let mut cx = Context::from_waker(&waker);
            match future.as_mut().poll(&mut cx) {
                Poll::Pending => *slot = Some(future),
                Poll::Ready(()) => {
                    self.outstanding.fetch_sub(1, Ordering::SeqCst);
                }
            }
        }
    }
}

struct ThreadWaker(thread::Thread);

impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) {
        self.0.unpark();
    }

    fn wake_by_ref(self: &Arc<Self>) {
        self.0.unpark();
    }
}

pub fn block_on<F: Future>(future: F) -> F::Output {
    let mut future = std::pin::pin!(future);
    let waker = Waker::from(Arc::new(ThreadWaker(thread::current())));
    let mut cx = Context::from_waker(&waker);
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(value) => return value,
            Poll::Pending => thread::park(),
        }
    }
}

/// A future that completes after `duration`, waking the executor from a timer thread.
pub fn delay(duration: Duration) -> Delay {
    Delay { deadline: Instant::now() + duration, started: false }
}

pub struct Delay {
    deadline: Instant,
    started: bool,
}

impl Future for Delay {
    type Output = ();

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        let this = self.get_mut();
        if Instant::now() >= this.deadline {
            return Poll::Ready(());
        }
        if !this.started {
            this.started = true;
            let waker = cx.waker().clone();
            let deadline = this.deadline;
            thread::spawn(move || {
                let now = Instant::now();
                if deadline > now {
                    thread::sleep(deadline - now);
                }
                waker.wake();
            });
        }
        Poll::Pending
    }
}
