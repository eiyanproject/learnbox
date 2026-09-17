import json
import os
import sys
import threading


class KVStore:
    def __init__(self, path):
        self.path = os.fspath(path)
        self._lock = threading.Lock()
        self._data = {}
        open(self.path, "a").close()
        self._replay()
        self._file = open(self.path, "a", encoding="utf-8")

    def _replay(self):
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    break  # a torn final write
                if entry["op"] == "set":
                    self._data[entry["key"]] = entry["value"]
                elif entry["op"] == "del":
                    self._data.pop(entry["key"], None)

    def _append(self, entry):
        self._file.write(json.dumps(entry) + "\n")
        self._file.flush()

    def set(self, key, value):
        with self._lock:
            self._append({"op": "set", "key": key, "value": value})
            self._data[key] = value

    def get(self, key, default=None):
        with self._lock:
            return self._data.get(key, default)

    def delete(self, key):
        with self._lock:
            if key not in self._data:
                return False
            self._append({"op": "del", "key": key})
            del self._data[key]
            return True

    def keys(self):
        with self._lock:
            return sorted(self._data)

    def __len__(self):
        with self._lock:
            return len(self._data)

    def __contains__(self, key):
        with self._lock:
            return key in self._data

    def log_entries(self):
        with self._lock:
            self._file.flush()
            with open(self.path, encoding="utf-8") as f:
                return sum(1 for _ in f)

    def compact(self):
        with self._lock:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                for key, value in self._data.items():
                    f.write(json.dumps({"op": "set", "key": key, "value": value}) + "\n")
                f.flush()
                os.fsync(f.fileno())
            self._file.close()
            os.replace(tmp, self.path)
            self._file = open(self.path, "a", encoding="utf-8")

    def close(self):
        with self._lock:
            if not self._file.closed:
                self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def main(argv):
    if len(argv) < 2:
        print("usage: kvstore.py DB (set KEY VALUE | get KEY | del KEY | keys | compact)", file=sys.stderr)
        return 2
    db, command, *args = argv
    with KVStore(db) as store:
        if command == "set" and len(args) == 2:
            store.set(args[0], args[1])
            print("OK")
        elif command == "get" and len(args) == 1:
            if args[0] not in store:
                print(f"not found: {args[0]}", file=sys.stderr)
                return 1
            print(store.get(args[0]))
        elif command == "del" and len(args) == 1:
            print(1 if store.delete(args[0]) else 0)
        elif command == "keys" and not args:
            for key in store.keys():
                print(key)
        elif command == "compact" and not args:
            before = store.log_entries()
            store.compact()
            print(f"compacted {before} -> {store.log_entries()}")
        else:
            print(f"unknown command: {command}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
