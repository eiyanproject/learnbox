import json

import pytest

from api import device_names, interfaces_down, summarise, to_json

# Shaped the way a controller's inventory endpoint actually answers.
PAYLOAD = json.loads(
    """
{
  "devices": [
    {"hostname": "sw1", "role": "switch", "reachable": true,
     "interfaces": [{"name": "Fa0/1", "status": "up"},
                    {"name": "Fa0/2", "status": "down"}]},
    {"hostname": "sw2", "role": "switch", "reachable": true,
     "interfaces": [{"name": "Fa0/1", "status": "up"}]},
    {"hostname": "r1", "role": "router", "reachable": false,
     "interfaces": [{"name": "Gi0/0", "status": "up"},
                    {"name": "Gi0/1", "status": "administratively down"}]}
  ]
}
"""
)


def test_json_maps_onto_python_types():
    assert isinstance(PAYLOAD["devices"], list)
    assert PAYLOAD["devices"][0]["reachable"] is True
    assert PAYLOAD["devices"][2]["reachable"] is False


def test_device_names_keeps_api_order():
    assert device_names(PAYLOAD) == ["sw1", "sw2", "r1"]


def test_device_names_on_an_empty_inventory():
    assert device_names({"devices": []}) == []


def test_interfaces_down_finds_both_kinds():
    found = interfaces_down(PAYLOAD)
    assert ("sw1", "Fa0/2") in found
    assert ("r1", "Gi0/1") in found, "'administratively down' is not 'up' either"


def test_interfaces_down_excludes_working_ones():
    found = interfaces_down(PAYLOAD)
    assert ("sw2", "Fa0/1") not in found
    assert len(found) == 2


def test_interfaces_down_handles_a_device_with_no_interfaces():
    assert interfaces_down({"devices": [{"hostname": "x"}]}) == []


def test_summarise_by_role():
    assert summarise(PAYLOAD, "role") == {"switch": 2, "router": 1}


def test_summarise_by_reachability():
    assert summarise(PAYLOAD, "reachable") == {True: 2, False: 1}


def test_to_json_is_deterministic():
    a = {"b": 1, "a": 2}
    b = {"a": 2, "b": 1}
    assert to_json(a) == to_json(b), "sorted keys make equal payloads compare equal"


def test_to_json_round_trips():
    assert json.loads(to_json(PAYLOAD)) == PAYLOAD
