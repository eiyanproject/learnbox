import json


def device_names(payload):
    return [device["hostname"] for device in payload["devices"]]


def interfaces_down(payload):
    return [
        (device["hostname"], iface["name"])
        for device in payload["devices"]
        for iface in device.get("interfaces", [])
        if iface.get("status") != "up"
    ]


def summarise(payload, key):
    counts = {}
    for device in payload["devices"]:
        value = device.get(key)
        counts[value] = counts.get(value, 0) + 1
    return counts


def to_json(payload):
    return json.dumps(payload, sort_keys=True)
