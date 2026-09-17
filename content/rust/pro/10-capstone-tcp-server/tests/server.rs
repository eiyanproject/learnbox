use std::io::{BufRead, BufReader, Write};
use std::net::TcpStream;
use std::thread;
use std::time::Duration;

use tcp_kv_server::*;

struct Client {
    reader: BufReader<TcpStream>,
    writer: TcpStream,
}

impl Client {
    fn connect(port: u16) -> Client {
        let stream = TcpStream::connect(("127.0.0.1", port)).expect("server not accepting");
        stream.set_read_timeout(Some(Duration::from_secs(5))).unwrap();
        Client { reader: BufReader::new(stream.try_clone().unwrap()), writer: stream }
    }

    fn ask(&mut self, line: &str) -> String {
        writeln!(self.writer, "{line}").unwrap();
        self.writer.flush().unwrap();
        let mut reply = String::new();
        self.reader.read_line(&mut reply).unwrap();
        reply.trim_end().to_string()
    }
}

fn started() -> (Server, u16) {
    let mut server = Server::new();
    let port = server.start("127.0.0.1", 0).expect("bind failed");
    assert!(port > 0, "start() must return the bound port");
    (server, port)
}

#[test]
fn set_get_del_keys() {
    let (mut server, port) = started();
    let mut c = Client::connect(port);
    assert_eq!(c.ask("PING"), "PONG");
    assert_eq!(c.ask("GET missing"), "NIL");
    assert_eq!(c.ask("SET name Ana Wijaya"), "OK");
    assert_eq!(c.ask("GET name"), "Ana Wijaya");
    assert_eq!(c.ask("SET city Jakarta"), "OK");
    assert_eq!(c.ask("KEYS"), "city name");
    assert_eq!(c.ask("DEL name"), "1");
    assert_eq!(c.ask("DEL name"), "0");
    assert_eq!(server.store_len(), 1);
    server.stop();
}

#[test]
fn unknown_commands_keep_the_connection() {
    let (mut server, port) = started();
    let mut c = Client::connect(port);
    assert_eq!(c.ask("FLY away"), "ERR unknown command");
    assert_eq!(c.ask("GET"), "ERR unknown command");
    assert_eq!(c.ask(""), "ERR unknown command");
    assert_eq!(c.ask("PING"), "PONG");
    server.stop();
}

#[test]
fn quit_closes_the_connection() {
    let (mut server, port) = started();
    let mut c = Client::connect(port);
    assert_eq!(c.ask("QUIT"), "BYE");
    let mut rest = String::new();
    assert_eq!(c.reader.read_line(&mut rest).unwrap(), 0, "the server should close after BYE");
    server.stop();
}

#[test]
fn many_clients_share_the_store() {
    let (mut server, port) = started();
    let handles: Vec<_> = (0..8)
        .map(|i| {
            thread::spawn(move || {
                let mut c = Client::connect(port);
                for n in 0..25 {
                    assert_eq!(c.ask(&format!("SET k{i}-{n} {n}")), "OK");
                }
                assert_eq!(c.ask(&format!("GET k{i}-0")), "0");
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    assert_eq!(server.store_len(), 200);
    server.stop();
}

#[test]
fn execute_works_without_a_socket() {
    let store: Store = Default::default();
    assert_eq!(execute(&store, "SET a 1"), ("OK".to_string(), false));
    assert_eq!(execute(&store, "get a"), ("1".to_string(), false));
    assert_eq!(execute(&store, "QUIT").1, true);
}

#[test]
fn stop_is_idempotent_and_frees_the_port() {
    let (mut server, port) = started();
    Client::connect(port);
    server.stop();
    server.stop();
    thread::sleep(Duration::from_millis(50));
    assert!(TcpStream::connect(("127.0.0.1", port)).is_err(), "the listener should be closed");
}
