---
title: Interfaces and addresses
summary: Enter configuration mode, give an interface an address, and bring it up - the four commands every later lesson assumes.
order: 1
files: [r1.ios]
run: python lab.py
hints:
  - "Order matters. `interface GigabitEthernet0/0` first, then the address, then `no shutdown` - you cannot set an address without selecting an interface."
  - "The mask is written in full, not as a prefix length: `ip address 192.168.1.1 255.255.255.0`, not `/24`."
  - "Router interfaces ship administratively down. Without `no shutdown` the address is configured and the link still does not pass traffic - `show ip interface brief` says `administratively down`."
  - "You only need GigabitEthernet0/0 in this lesson. PC1 is already configured and already points at 192.168.1.1 as its gateway."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **interface** | a router port that carries traffic once it has an address |
| **IOS mode** | where you are in the command tree; the prompt shows it |
| **user mode** | `R1>`: look, do not touch |
| **privileged (enable) mode** | `R1#`: show everything, reload, save |
| **global configuration** | `R1(config)#`: change the device |
| **interface configuration** | `R1(config-if)#`: change one interface |
| **mask** | `255.255.255.0`, written out in full here |
| **administratively down** | an interface nobody has brought up; router interfaces start like this |
| **`no` form** | `no <command>` undoes a command |
| **Status** / **Protocol** | physical and administrative state / whether the line is usable; both must say `up` |
| **default gateway** | the router address a PC sends other-subnet traffic to |
| **topology** | the lab's layout of devices and cables |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python lab.py` | applies your configuration to the lab topology and runs the pings |
| `netlab console one-router R1` | opens an interactive console on R1 |
### IOS commands

| Command | What it does |
|---|---|
| `enable` | user mode to privileged mode |
| `configure terminal` | privileged to global configuration |
| `interface GigabitEthernet0/0` | selects an interface |
| `ip address 192.168.1.1 255.255.255.0` | sets its address |
| `no shutdown` | brings it up |
| `exit`, `end` | up one level / all the way back to `#` |
| `show ip interface brief` | each interface's address, status and protocol |
| `show running-config` | the configuration in use |

---

A router interface with no address does nothing. Giving it one takes four
commands, and every lesson after this assumes you can type them without
thinking.

## The modes

IOS has modes, and the prompt tells you which one you are in:

```
R1>                      user mode - look, do not touch
R1#                      privileged (enable) mode - show everything, reload, save
R1(config)#              global configuration - change the device
R1(config-if)#           interface configuration - change one interface
```

You move down with `enable`, `configure terminal`, `interface <name>`, and back
up with `exit` (one level) or `end` (all the way to `#`).

This matters more than it looks. `ip address ...` typed at `R1(config)#` is
rejected, because addresses belong to interfaces, not to the device. The
mode **is** the context.

## The four commands

```
enable
configure terminal
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
```

Three things that catch people out:

- **The mask is written out in full.** `255.255.255.0`, not `/24`. IOS accepts
  prefix notation in some places, but not here.
- **`no shutdown` is not optional.** Router interfaces arrive administratively
  down. The address will be configured, `show running-config` will look
  perfect, and nothing will pass. Switch ports are the opposite: they come up
  by default.
- **`no <command>` undoes things generally.** `no ip address` removes the
  address; `no shutdown` removes the shutdown. It is one idea, not two
  commands.

## Checking your work

```
show ip interface brief
```

```
Interface               IP-Address       OK? Status                Protocol
GigabitEthernet0/0      192.168.1.1      YES up                    up
GigabitEthernet0/1      unassigned       YES administratively down down
```

Two columns, two different questions. **Status** is the physical/administrative
state — `administratively down` means you have not typed `no shutdown`.
**Protocol** is whether the line is actually usable. Both must say `up`.

## Your turn

The topology is `one-router`: PC1 and PC2 each on their own subnet, with R1
between them. PC1 is already configured with 192.168.1.10/24 and a default
gateway of 192.168.1.1.

In `r1.ios`, configure **GigabitEthernet0/0** so that PC1 can reach the router:

- address 192.168.1.1, mask 255.255.255.0
- the interface up

Run `python lab.py` to see what your config achieves, or explore interactively:

```
netlab console one-router R1
```
