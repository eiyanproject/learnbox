import json
import threading

from kvstore import KVStore, main


def test_basic_operations(tmp_path):
    with KVStore(tmp_path / "db") as db:
        db.set("name", "Ana")
        db.set("profile", {"age": 31, "tags": ["a", "b"]})
        assert db.get("name") == "Ana"
        assert db.get("profile") == {"age": 31, "tags": ["a", "b"]}
        assert db.get("missing") is None and db.get("missing", 0) == 0
        assert "name" in db and "missing" not in db
        assert len(db) == 2
        assert db.keys() == ["name", "profile"]


def test_delete(tmp_path):
    with KVStore(tmp_path / "db") as db:
        db.set("a", 1)
        assert db.delete("a") is True
        assert db.delete("a") is False
        assert "a" not in db
        assert db.log_entries() == 2, "deleting a missing key must not write"


def test_persists_across_reopen(tmp_path):
    path = tmp_path / "db"
    with KVStore(path) as db:
        db.set("a", 1)
        db.set("b", 2)
        db.set("a", 3)
        db.delete("b")
    with KVStore(path) as db:
        assert db.get("a") == 3
        assert "b" not in db
        assert db.log_entries() == 4


def test_log_is_json_lines(tmp_path):
    path = tmp_path / "db"
    with KVStore(path) as db:
        db.set("k", "v")
        db.delete("k")
    lines = [json.loads(l) for l in path.read_text().splitlines()]
    assert lines == [{"op": "set", "key": "k", "value": "v"}, {"op": "del", "key": "k"}]


def test_recovers_from_torn_final_line(tmp_path):
    path = tmp_path / "db"
    with KVStore(path) as db:
        db.set("safe", "yes")
    with open(path, "a") as f:
        f.write('{"op": "set", "key": "half", "va')
    with KVStore(path) as db:
        assert db.get("safe") == "yes"
        assert "half" not in db


def test_compaction(tmp_path):
    path = tmp_path / "db"
    with KVStore(path) as db:
        for i in range(100):
            db.set("counter", i)
        db.set("other", "x")
        db.set("gone", 1)
        db.delete("gone")
        assert db.log_entries() == 103
        db.compact()
        assert db.log_entries() == 2
        db.set("after", True)
    with KVStore(path) as db:
        assert db.get("counter") == 99 and db.get("other") == "x" and db.get("after") is True
        assert "gone" not in db
    assert not (tmp_path / "db.tmp").exists()


def test_thread_safe_writes(tmp_path):
    path = tmp_path / "db"
    with KVStore(path) as db:

        def writer(n):
            for i in range(200):
                db.set(f"t{n}-{i}", i)

        threads = [threading.Thread(target=writer, args=(n,)) for n in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(db) == 1200
    with KVStore(path) as db:
        assert len(db) == 1200
        assert db.log_entries() == 1200


def test_cli(tmp_path, capsys):
    db = str(tmp_path / "cli.db")
    assert main([db, "set", "greeting", "hello world"]) == 0
    assert main([db, "get", "greeting"]) == 0
    assert main([db, "set", "a", "1"]) == 0
    assert main([db, "keys"]) == 0
    assert main([db, "del", "a"]) == 0
    assert main([db, "del", "a"]) == 0
    out = capsys.readouterr().out
    assert out == "OK\nhello world\nOK\na\ngreeting\n1\n0\n"
    assert main([db, "get", "nope"]) == 1
    assert "not found: nope" in capsys.readouterr().err
    assert main([db, "compact"]) == 0
    assert capsys.readouterr().out == "compacted 3 -> 1\n"
