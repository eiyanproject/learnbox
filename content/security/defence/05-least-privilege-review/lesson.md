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

The principle of **least privilege** - grant the minimum access needed - is easy
to state and hard to maintain, because access only ever seems to get *added*.
Someone needs admin for a one-off task and keeps it; a role accumulates
permissions nobody remembers the reason for. Over time every account holds more
than it should, and each excess privilege is extra damage available to an
attacker who compromises it. The defence is a recurring **review**.

## Two questions

**Does this account hold more than its role allows?** Compare each account's
privileges against the set permitted for its role. Anything beyond that is
**excess** - a grant that should be revoked, or a role that should be changed.
A support account with database-admin rights is exactly the kind of finding this
surfaces.

**Does this account use everything it was granted?** A privilege held but never
exercised is pure risk with no benefit - revoke it. Comparing granted against
actually-used privileges finds these, and it is how cloud IAM right-sizing
tools work: watch what is used, strip the rest.

Both reduce the **blast radius** - how much an attacker gains by taking one
account. That is the whole point of least privilege: assume a breach, and make
each one worth as little as possible.

## Your turn

In `privreview.py` (an account is `{'role': ..., 'privileges': [...]}`):

- `excess(account, allowed_by_role)` - the sorted privileges the account holds
  beyond what its role allows
- `review(accounts, allowed_by_role)` - a dict of account name to its excess, for
  only the accounts that have any
- `unused(account, used)` - the sorted privileges granted but not in `used`
