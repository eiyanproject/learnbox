use std::future::Future;
use std::pin::Pin;
use std::sync::mpsc::{Receiver, Sender};
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

pub struct Executor {
    // ready queue and a way to know when everything is finished
}

impl Executor {
    pub fn new() -> Self {
        todo!()
    }

    pub fn spawn<T, F>(&self, future: F) -> JoinHandle<T>
    where
        F: Future<Output = T> + Send + 'static,
        T: Send + 'static,
    {
        todo!()
    }

    pub fn run(&self) {
        todo!()
    }
}

pub fn block_on<F: Future>(future: F) -> F::Output {
    todo!()
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
