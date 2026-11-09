---
title: IAM users, groups and the root user
summary: Who can sign in, how permissions reach them through groups, what to do with the root user, and a password policy - the shape of access in one account.
order: 2
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`aws iam create-group --group-name developers`, then `aws iam create-user --user-name alice`, then `aws iam add-user-to-group --group-name developers --user-name alice`."
  - "AWS managed policies live under the account `aws`: `arn:aws:iam::aws:policy/ReadOnlyAccess`. Attach it to the group with `aws iam attach-group-policy --group-name developers --policy-arn ...`."
  - "The check refuses policies attached straight to a user. Permissions go on the group; users get them by being in it."
  - "`aws iam update-account-password-policy --minimum-password-length 14 --require-symbols --require-numbers --require-uppercase-characters --require-lowercase-characters`."
---

**IAM** (Identity and Access Management) decides who can do what in an
account. It is global - not tied to a Region - and it costs nothing.

## The root user

Every account starts with one identity: the **root user**, the email
address the account was opened with. Root can do everything, including
things no policy can grant or take away (closing the account, changing the
support plan). So it is used for almost nothing:

- turn on **MFA** for it straight away;
- create **no access keys** for it - ever;
- lock the credentials away and work as something else.

The exam asks about this often. "Least privilege" starts with not using root.

## Users, groups and policies

An **IAM user** is a long-lived identity in the account: a person signing in
to the console, or (less and less) a program with access keys. A **group**
is a set of users. A **policy** is a JSON document that allows or denies
actions on resources.

Policies attach to users, groups or roles. Attach them to **groups**, not to
users: when Alice changes team, you move her between groups instead of
untangling permissions one user at a time.

```
aws iam create-group --group-name developers
aws iam create-user --user-name alice
aws iam add-user-to-group --group-name developers --user-name alice
aws iam attach-group-policy --group-name developers \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
```

`ReadOnlyAccess` is an **AWS managed policy**: written and maintained by AWS,
its ARN has `aws` where an account number would be. You write **customer
managed policies** yourself - next lesson.

## Where people really sign in

For an organisation with more than a handful of people, long-lived IAM users
are the old way. **IAM Identity Center** gives people one sign-in (or your
existing directory, federated in) and hands out short-lived credentials for
each account they may use. IAM users remain for the odd case and for
learning how permissions work - which is why they are here.

## A password policy

The account's **password policy** applies to every IAM user's console
password: length, character types, maximum age, reuse.

```
aws iam update-account-password-policy --minimum-password-length 14 \
  --require-symbols --require-numbers \
  --require-uppercase-characters --require-lowercase-characters
```

## Your task

Fill in `setup.sh` so that it:

1. creates a group **`developers`** with the AWS managed policy
   **`ReadOnlyAccess`** attached;
2. creates users **`alice`** and **`bob`**, both in `developers`, with
   **no policies of their own**;
3. sets the password policy: at least **14** characters, and symbols,
   numbers, upper and lower case all required.

Afterwards, `aws iam get-account-authorization-details --query
'UserDetailList[].[UserName,GroupList]'` shows the whole picture in one call.
