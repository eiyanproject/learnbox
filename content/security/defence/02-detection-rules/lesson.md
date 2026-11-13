---
title: Writing a detection rule
summary: Detection turns knowledge of an attack into a rule that fires when it happens. This is what a SIEM and an IDS run on.
order: 2
files: [detect.py]
run: python detect.py
hints:
  - "A rule is `{'name': ..., 'when': {field: value, ...}}`. It matches an event when every field in `when` equals the event's value for that field."
  - "`matches`: all of the rule's `when` fields must match; a field the rule omits is not checked."
  - "`alerts`: for every rule and every event it matches, produce `(rule_name, event)`."
  - "`threshold_alert`: count how many events match a rule's `when`, and fire only when the count exceeds the rule's `count` - this catches bursts like brute force."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **detection rule** | a description of what an attack looks like in logs, which raises an alert when it appears |
| **event** | one parsed log entry, as named fields: `user`, `result`, `ip` |
| **alert** | the notice a rule raises when it matches |
| **blue team** | the defenders; the attackers in an exercise are the red team |
| **SIEM** | Security Information and Event Management: the system that collects logs from everywhere and runs rules on them |
| **IDS** | intrusion detection system: watches network traffic or a host for attacks |
| **signature rule** | a rule that matches the fields of a single event |
| **threshold rule** | a rule that fires only when enough events match, such as 50 failed logins |
| **broad / narrow rule** | names few fields and matches a lot; names many fields and matches little |
| **false positive** | an alert for harmless activity |
| **false negative** | an attack the rule missed |
| **tuning** | adjusting a rule until it catches the attack without too many false positives |
| **Sigma** | an open, YAML-based format for writing detection rules that work in many SIEMs |
| **YAML** | a readable text format for structured data, using indentation |
| **logsource** | in Sigma, which kind of log a rule applies to |
| **selection** | in Sigma, the field values to look for |
| **condition** | in Sigma, how selections combine: `selection and not filter` |
| **level** | in Sigma, how serious a match is: informational, low, medium, high, critical |
| **correlation** | linking several events, such as failures followed by a success |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python detect.py` | runs your program: one signature rule and one threshold rule |

### Python names

| Name | What it does |
|---|---|
| `{"name": ..., "when": {...}}` | one rule: a name, and the fields an event must have |
| `rule["when"].items()` | each `(field, value)` the rule requires |
| `event.get(field) == value` | the event has that value (a missing field gives `None`) |
| `all(...)` | `True` when every test passes (and for an empty list) |
| `out.append((rule["name"], event))` | records one alert |
| `sum(1 for event in events if ...)` | counts the events that pass the test |
| `count > rule["count"]` | more than the rule's limit |
| `[{"result": "FAILED"}] * 8` | a list of eight identical events |

---

Every attack you now recognise can be turned into a **detection rule**: a
description of what the attack looks like in the logs, which raises an
**alert** automatically when it appears. Rules are the engine inside a
**SIEM** (the system that gathers logs from every machine and runs rules on
them), inside intrusion detection systems, and inside every alerting
pipeline. Writing good rules is a core **blue-team** (defender) skill.

## Signature rules

The simplest rule matches fields of a single **event**:

```python
{"name": "root login", "when": {"user": "root", "result": "OK"}}
```

"Alert when someone logs in successfully as `root`." An event matches when
**every** field named in `when` has that value in the event. Fields the rule
does not mention are not checked at all, so the event above can have any
`ip`, any `ts`, anything else.

That makes a rule as **broad** or as **narrow** as you choose:

| Rule `when` | Catches |
|---|---|
| `{"result": "FAILED"}` | every failed login: far too much to read |
| `{"user": "root", "result": "OK"}` | every successful root login: rare, worth a look |
| `{"user": "root", "result": "OK", "ip": "10.0.0.9"}` | only from one address: misses the same attack from anywhere else |

The skill is catching the attack (no **false negatives**) without drowning in
alerts for harmless activity (**false positives**). Adjusting a rule towards
that balance is called **tuning**.

## Threshold rules

Some attacks are invisible in one event and obvious in many. One failed login
is nothing; fifty from one address in a minute is a brute force. A
**threshold rule** counts the matching events and fires only when the count
passes a limit:

```text
rule:   result = FAILED, count > 5
events: FAILED x 8        ->  alert
events: FAILED x 3        ->  nothing
```

It is the same shape as the scan detection in Network lesson 3 and the
brute-force check in Forensics lesson 1, made general.

## Real rules: Sigma

**Sigma** is an open format for detection rules, written in YAML, that can be
converted to the query language of most SIEMs. A rule for the successful root
login above would look roughly like this:

```text
title: Successful SSH login as root
logsource:
  product: linux
  service: sshd
detection:
  selection:
    user: root
    result: OK
  condition: selection
falsepositives:
  - an administrator's planned maintenance
level: high
```

The parts match what you are building. `selection` is the `when`: its fields
must all match. `condition` says how selections combine, with `and`, `or` and
`not`, as in `selection and not filter` to leave out known harmless cases.
`falsepositives` writes down what else can trigger it, and `level` says how
serious it is. The Sigma specification says `high` and `critical` alerts
should be reviewed promptly, while `low` ones are reviewed regularly.

Real rule languages add timing windows, wildcards, regular expressions and
**correlation** between events. But the core is what you write here: describe
the pattern, count the matches, fire when it is met.

## Your turn

In `detect.py`:

- `matches(rule, event)`: does the event have every field value in the
  rule's `when`?
- `alerts(rules, events)`: a list of `(rule_name, event)` for every match of
  every rule.
- `threshold_alert(rule, events)`: `True` when the number of events matching
  the rule's `when` is **more than** the rule's `count`.

Run it:

```text
alerts: [('root login', {'user': 'root', 'result': 'OK', 'ip': '10.0.0.9'})]
burst? True
```

## Check yourself

1. A rule's `when` is `{"user": "root"}`. Does an event with `"ip":
   "1.2.3.4"` and `"user": "root"` match?
   *Yes: the rule does not check `ip`.*
2. What is a false positive?
   *An alert for harmless activity.*
3. Why is one failed login not worth an alert, but fifty are?
   *Fifty in a short time is a brute-force pattern; one is a typo.*
4. In Sigma, what does `condition: selection and not filter` do?
   *Matches the selection, except events that also match the filter.*
5. What does the `level` field say?
   *How serious a match is, and how fast it should be reviewed.*
