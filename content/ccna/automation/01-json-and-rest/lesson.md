---
title: JSON, REST and talking to a controller
summary: The data format every network API speaks, the four verbs, and reading a device inventory without clicking anything.
order: 1
files: [api.py]
run: python -i api.py
hints:
  - "`json.loads(text)` turns a JSON string into Python: object becomes dict, array becomes list, true/false become True/False, null becomes None."
  - "`device_names` should keep the order the API returned them in - a list comprehension over the list does that; sorting would throw away information the caller may want."
  - "`interfaces_down` looks at each device's `interfaces` list and collects those whose `status` is not `\"up\"`. Return `(device, interface)` tuples."
  - "`summarise` counts by a key: build a dict with `counts[value] = counts.get(value, 0) + 1`."
---

Ten devices can be configured by hand. Ten thousand cannot, and the industry
answer is that devices expose an API and you write code against it. The exam
does not ask you to be a programmer, but it does ask you to recognise JSON,
know the REST verbs, and understand what a controller is for.

## JSON

JSON is the format almost every network API returns. It maps onto Python
almost exactly:

| JSON | Python |
|---|---|
| object `{...}` | `dict` |
| array `[...]` | `list` |
| string | `str` |
| number | `int` / `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

```python
import json
data = json.loads(text)      # text  -> Python
text = json.dumps(data)      # Python -> text
```

Two things that catch people: JSON keys are **always strings**, and JSON has
no trailing commas and no comments. A configuration file that looks like JSON
but has a comment in it is YAML or JSON5, not JSON.

## REST

A REST API is a set of URLs you act on with HTTP verbs:

| Verb | Means | Idempotent |
|---|---|---|
| GET | read | yes |
| POST | create | no |
| PUT | replace | yes |
| PATCH | modify part | no (usually) |
| DELETE | remove | yes |

**Idempotent** means doing it twice has the same effect as doing it once. It
matters because networks lose replies: if you POST twice because the first
response was lost, you may create two of something. This is why configuration
tooling prefers PUT-shaped operations.

Responses carry a status code: 2xx worked, 4xx you got it wrong, 5xx the server
got it wrong. 401 is "who are you", 403 is "I know who you are and no".

## Controllers

Traditional networking configures each device separately; the control plane
(deciding where traffic goes) lives on every box. **Controller-based**
networking moves those decisions to one place, and the devices become the data
plane that carries out instructions.

| | Traditional | Controller-based |
|---|---|---|
| Control plane | on each device | centralised |
| Configured by | CLI, per device | API, once |
| Consistency | up to you | enforced |
| Failure mode | one device | possibly all of them |

Cisco's is DNA Center; the exam also expects you to recognise Ansible, Puppet
and Chef as configuration management tools, and that **Ansible is agentless**
and pushes over SSH, while Puppet and Chef traditionally pull with an agent
installed on the target.

## Your turn

In `api.py`, work with a device inventory exactly as an API would return it:

- `device_names(payload)`: the hostnames, in the order the API gave them
- `interfaces_down(payload)`: `(device, interface)` tuples for every interface
  whose status is not `"up"`
- `summarise(payload, key)`: how many devices have each value of `key`, as a
  dict — e.g. `summarise(payload, "role")` gives `{"switch": 2, "router": 1}`
- `to_json(payload)`: the payload serialised with sorted keys, so two equal
  payloads always produce the same text
