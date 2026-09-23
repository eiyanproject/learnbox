import json
import re
import statistics
from datetime import date


def summarise(values):
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stdev": round(statistics.pstdev(values), 3),
    }


def date_facts(iso):
    d = date.fromisoformat(iso)
    return {
        "formatted": d.strftime("%Y/%m/%d"),
        "weekday": d.weekday(),
        "day_of_year": d.timetuple().tm_yday,
        "is_weekend": d.weekday() >= 5,
    }


def find_codes(text):
    return re.findall(r"[A-Z]{2}\d{3}", text)


def round_trip(obj):
    text = json.dumps(obj, sort_keys=True)
    return text, json.loads(text)
