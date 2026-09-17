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

// T: Unpin so `self.get_mut()` is allowed; every practical output type is.
impl<T: Unpin> Future for Ready<T> {
    type Output = T;

    fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<T> {
        Poll::Ready(self.get_mut().0.take().expect("polled after completion"))
    }
}

pub struct Delay {
    deadline: Instant,
    started: bool,
}

pub fn delay(duration: Duration) -> Delay {
    Delay { deadline: Instant::now() + duration, started: false }
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

pub struct Counter {
    remaining: usize,
    polls: usize,
}

pub fn counter(n: usize) -> Counter {
    Counter { remaining: n, polls: 0 }
}

impl Future for Counter {
    type Output = usize;

    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<usize> {
        let this = self.get_mut();
        this.polls += 1;
        if this.remaining == 0 {
            return Poll::Ready(this.polls);
        }
        this.remaining -= 1;
        cx.waker().wake_by_ref(); // there is progress to make right away
        Poll::Pending
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
