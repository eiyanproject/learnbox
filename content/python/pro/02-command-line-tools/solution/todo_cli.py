import argparse
import json
import sys
from pathlib import Path


def build_parser():
    parser = argparse.ArgumentParser(prog="todo", description="A tiny to-do list.")
    parser.add_argument("--file", default="todo.json", help="task storage (JSON)")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add a task")
    add.add_argument("title")
    add.add_argument("--priority", type=int, choices=range(1, 4), default=2)

    ls = sub.add_parser("list", help="show tasks")
    ls.add_argument("--all", action="store_true", help="include finished tasks")

    done = sub.add_parser("done", help="mark a task finished")
    done.add_argument("id", type=int)
    return parser


def load(path):
    return json.loads(path.read_text()) if path.exists() else []


def save(path, tasks):
    path.write_text(json.dumps(tasks, indent=2))


def main(argv=None):
    args = build_parser().parse_args(argv)
    path = Path(args.file)
    tasks = load(path)

    if args.command == "add":
        new_id = max((t["id"] for t in tasks), default=0) + 1
        tasks.append({"id": new_id, "title": args.title, "priority": args.priority, "done": False})
        save(path, tasks)
        print(f"added {new_id}")
        return 0

    if args.command == "list":
        shown = [t for t in tasks if args.all or not t["done"]]
        for t in sorted(shown, key=lambda t: (-t["priority"], t["id"])):
            mark = "x" if t["done"] else " "
            print(f"[{mark}] {t['id']} (p{t['priority']}) {t['title']}")
        return 0

    if args.command == "done":
        for t in tasks:
            if t["id"] == args.id:
                t["done"] = True
                save(path, tasks)
                print(f"done {args.id}")
                return 0
        print(f"error: no task {args.id}", file=sys.stderr)
        return 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
