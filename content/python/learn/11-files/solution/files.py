import csv
import json
from pathlib import Path


def count_lines(path):
    with open(path) as f:
        return sum(1 for line in f if line.strip())


def write_report(path, scores):
    with open(path, "w") as f:
        for name, score in sorted(scores.items()):
            f.write(f"{name}: {score}\n")


def average_score(csv_path):
    with open(csv_path, newline="") as f:
        scores = [float(row["score"]) for row in csv.DictReader(f)]
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 1)


def update_settings(path, changes):
    path = Path(path)
    settings = json.loads(path.read_text()) if path.exists() else {}
    settings.update(changes)
    path.write_text(json.dumps(settings, indent=2))
    return settings
