def matches(rule, event):
    # Every field the rule specifies must match; unmentioned fields are free.
    return all(event.get(field) == value for field, value in rule["when"].items())


def alerts(rules, events):
    out = []
    for rule in rules:
        for event in events:
            if matches(rule, event):
                out.append((rule["name"], event))
    return out


def threshold_alert(rule, events):
    # Some attacks only show up in aggregate: count the matches and fire once
    # they cross the line. This is the brute-force / scan shape, generalised.
    count = sum(1 for event in events if matches(rule, event))
    return count > rule["count"]


if __name__ == "__main__":
    rules = [{"name": "root login", "when": {"user": "root", "result": "OK"}}]
    events = [{"user": "root", "result": "OK", "ip": "10.0.0.9"}]
    print("alerts:", alerts(rules, events))
    brute = {"name": "brute force", "when": {"result": "FAILED"}, "count": 5}
    print("burst?", threshold_alert(brute, [{"result": "FAILED"}] * 8))
