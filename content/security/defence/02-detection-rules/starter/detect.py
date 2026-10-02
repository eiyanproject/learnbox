def matches(rule, event):
    pass


def alerts(rules, events):
    pass


def threshold_alert(rule, events):
    pass


if __name__ == "__main__":
    rules = [{"name": "root login", "when": {"user": "root", "result": "OK"}}]
    events = [{"user": "root", "result": "OK", "ip": "10.0.0.9"}]
    print("alerts:", alerts(rules, events))
    brute = {"name": "brute force", "when": {"result": "FAILED"}, "count": 5}
    print("burst?", threshold_alert(brute, [{"result": "FAILED"}] * 8))
