---
title: Reviewing for least privilege
summary: Access tends to accumulate and never get taken away. Finding the privileges an account holds but should not is a recurring defensive audit.
order: 5
files: [privreview.py]
run: python privreview.py
hints:
  - "`excess`: the privileges an account holds that are not in the set allowed for its role. Return them as a sorted list."
  - "`allowed_by_role` maps a role name to the set of privileges that role may have; an account is `{'role': ..., 'privileges': [...]}`."
  - "`review`: the accounts that hold any excess privilege, each mapped to its sorted excess list - skip accounts that are clean."
  - "`unused`: privileges an account was granted but never actually used, given a set of the ones it used - the other half of least privilege."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **least privilege** | give each account only the access it needs, and nothing more |
| **privilege** (permission) | one thing an account is allowed to do, such as `db_admin` |
| **account** | a user, or a program's identity, that can sign in or act |
| **role** | a named job with a set of allowed privileges, such as `support` or `admin` |
| **grant** | giving an account a privilege |
| **revoke** | taking a privilege away |
| **privilege creep** | access piling up over time, because it is added and rarely removed |
| **access review** (audit) | regularly checking who has what, and taking away what they should not have |
| **excess privilege** | held by an account but not allowed for its role |
| **unused privilege** | granted, but never actually used |
| **right-sizing** | cutting an account's access down to what it really uses |
| **IAM** | identity and access management: a cloud provider's system of accounts, roles and permissions |
| **blast radius** | how much damage an attacker can do with one stolen account |
| **assume breach** | plan as if some account will be stolen, and limit what each one can do |
| **`wheel`** (or `sudo`) group | on Linux, the group whose members may run commands as root |
| **set difference** | the items in one set that are not in another |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `id` | shows your user and the groups you belong to |
| `getent group wheel` | lists the members of the `wheel` group, who may use `sudo` |
| `sudo -l` | lists what you may run with `sudo` |
| `python privreview.py` | runs your program: reviews two accounts against their roles |

### Python names

| Name | What it does |
|---|---|
| `{'role': ..., 'privileges': [...]}` | one account |
| `allowed_by_role` | a dict from role name to the set of privileges that role may have |
| `allowed_by_role.get(role, set())` | the role's allowed set, or an empty set for an unknown role |
| `set(a) - set(b)` | set difference: what is in `a` but not in `b` |
| `sorted(...)` | a sorted list |
| `for name, account in accounts.items():` | each account with its name |
| `if over:` | the list is not empty |

---

The principle of **least privilege**, give each account only the access it
needs, is easy to state and hard to keep. Access only ever seems to get
**added**. Someone needs admin rights for a one-off task and keeps them. A
role collects permissions nobody remembers the reason for. Over time, every
account holds more than it should. This is called **privilege creep**, and
each extra privilege is extra damage available to an attacker who steals that
account.

The defence is a regular **access review**.

## Question 1: does the account hold more than its role allows?

Each **role** has a set of allowed privileges. Compare each account's
privileges with the set for its role. Anything beyond it is an **excess
privilege**: either a grant to **revoke**, or a sign that the account needs a
different role.

```text
role support allows:  read_tickets, reply
alice (support) has:  read_tickets, reply, db_admin
excess:               db_admin
```

A support account with database-admin rights is exactly the kind of finding
this produces. In set terms it is a **set difference**: what the account has,
minus what the role allows.

An account whose role is not in the table at all is allowed nothing, so
everything it holds is excess. That is deny by default again (Web lesson 4).

## Question 2: does the account use everything it was granted?

A privilege that is held but never used is pure risk with no benefit. Revoke
it. Comparing what was **granted** with what was actually **used** finds these.
This is how cloud **IAM** right-sizing tools work: they watch which
permissions an account really uses over some weeks, and suggest removing the
rest.

## On a Linux machine

The same review applies to an ordinary server. `id` shows the groups you
belong to, and members of the `wheel` (or `sudo`) group can run anything as
root:

```text
$ getent group wheel
wheel:alice
```

Every name in that list is someone whose stolen password gives an attacker
the whole machine. Each one should have a reason to be there.

## Why it matters: blast radius

Both questions shrink the **blast radius**: how much an attacker gains by
taking over one account. That is the real point of least privilege. **Assume
a breach**: some account will be stolen one day, so make each account worth
as little as possible to whoever steals it.

## Your turn

In `privreview.py` (an account is `{'role': ..., 'privileges': [...]}`):

- `excess(account, allowed_by_role)`: the sorted privileges the account holds
  beyond what its role allows. A role missing from `allowed_by_role` allows
  nothing.
- `review(accounts, allowed_by_role)`: a dict from account name to its
  excess, for only the accounts that have any.
- `unused(account, used)`: the sorted privileges granted but not in `used`.

Run it:

```text
review: {'alice': ['db_admin']}
```

`bob` is not listed: that account holds less than its role allows, which is fine.

## Check yourself

1. What is privilege creep?
   *Access piling up because it is added and rarely removed.*
2. An account's role is `support`, which allows `read_tickets` and `reply`.
   It also has `db_admin`. What is the finding?
   *Excess privilege: `db_admin`.*
3. An account's role is not in the table. What does it allow?
   *Nothing: deny by default.*
4. Why revoke a privilege that is never used?
   *It adds risk and no benefit.*
5. What is the blast radius of an account?
   *How much damage an attacker can do with it.*
