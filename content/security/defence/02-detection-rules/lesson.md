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

Every attack you now recognise can be turned into a **detection rule**: a
description of what the attack looks like in the data, which fires automatically
when the pattern appears. This is the engine inside a SIEM, an intrusion
detection system, and every alerting pipeline - and writing good rules is a core
blue-team skill.

## Signature rules

The simplest rule matches fields of an event:

```python
{"name": "root login", "when": {"user": "root", "result": "OK"}}
```

An event matches when every field named in `when` equals the event's value.
Fields the rule does not mention are not checked, so a rule is as broad or as
narrow as you make it - and the art is making it catch the attack without
drowning you in false positives.

## Threshold rules

Some attacks are invisible in a single event and obvious in aggregate. One
failed login is nothing; fifty from one source in a minute is a brute force. A
**threshold rule** fires only when the number of matching events crosses a line
- the same shape as the scan detection from the network section, generalised.

Real rule languages (Sigma, Snort, the queries behind a SIEM) add timing,
regular expressions and correlation, but the core is this: describe the
pattern, count the matches, fire when it is met.

## Your turn

In `detect.py`:

- `matches(rule, event)` - does the event satisfy the rule's `when`?
- `alerts(rules, events)` - `(rule_name, event)` for every match
- `threshold_alert(rule, events)` - `True` when the number of events matching
  the rule's `when` exceeds the rule's `count`
