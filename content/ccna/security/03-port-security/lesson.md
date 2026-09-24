---
title: Port security and hardening the access layer
summary: Limiting which devices may use a switch port, and the three things to do to every switch before it ships.
order: 3
files: [sw1.ios]
run: python lab.py
hints:
  - "Port security only works on an access port, so `switchport mode access` must come first - IOS refuses the command on a port that could still negotiate a trunk."
  - "`switchport port-security` turns it on, `switchport port-security maximum 1` sets how many MAC addresses may use the port."
  - "`switchport port-security violation restrict` drops offending frames and logs; `shutdown` (the default) disables the port entirely."
  - "Fa0/1 and Fa0/2 get port security. Leave Fa0/3 and Fa0/4 alone so the tests can tell configured ports from unconfigured ones."
---

The access layer is where untrusted things get plugged in. Port security is the
switch's answer to "someone unplugged the printer and connected a laptop".

## What it does

```
interface FastEthernet0/1
 switchport mode access
 switchport port-security
 switchport port-security maximum 1
 switchport port-security violation restrict
```

The switch learns the MAC address of whatever is connected and refuses to serve
any other. `maximum 1` means one device; raise it where an IP phone has a PC
behind it, which is the usual real exception.

**`switchport mode access` is required first.** IOS will not enable port
security on a port that could still negotiate itself into a trunk, and the
error message when you try is not especially clear.

## The three violation modes

| Mode | Traffic | Port | Logged |
|---|---|---|---|
| `protect` | dropped | stays up | no |
| `restrict` | dropped | stays up | yes, counter increments |
| `shutdown` (default) | dropped | **err-disabled** | yes |

`shutdown` is the default and it is severe: the port goes err-disabled and
stays down until an administrator clears it, or a configured `errdisable
recovery` timer expires. A violation on an unattended port means a site visit.

`restrict` is usually the practical choice: the offending device is blocked,
the legitimate one keeps working, and you find out.

## Sticky addresses

```
switchport port-security mac-address sticky
```

Learns whatever is connected now and writes it into the running configuration,
so you do not have to type MAC addresses by hand. Convenient, and worth
remembering that it learns whatever happens to be plugged in at that moment —
including the wrong thing.

## The rest of hardening the access layer

Three habits, each answering a specific attack:

- **Shut unused ports.** An unconfigured port is in VLAN 1 and will happily
  serve anyone who finds a live socket in a meeting room.
- **Do not use VLAN 1 for anything.** It is where everything lands by default,
  so it is the VLAN an attacker can reach most easily.
- **Set the native VLAN to something unused.** Untagged frames on a trunk land
  in the native VLAN, which is the basis of VLAN hopping.

## Your turn

The `switched` topology. In `sw1.ios`:

- make Fa0/1 and Fa0/2 access ports with port security enabled
- allow a maximum of 1 MAC address on each
- set the violation mode to `restrict` on both

Leave Fa0/3 and Fa0/4 unconfigured.
