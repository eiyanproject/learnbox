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

An AWS account starts with one all-powerful identity, and a team needs many
people with different, limited access. **IAM** (Identity and Access
Management) is the service that decides **who** can do **what** in an
account. It is global, not tied to a Region, and costs nothing. This lesson
sets up the basic shape: what to do with the all-powerful identity, people as
**users**, permissions given to **groups**, and the account's password
rules.

## The root user

Every account starts with one identity: the **root user**, signed in with
the email address and password the account was opened with. Root can do
everything, including a few things no policy can grant or take away, such as
closing the account or changing the support plan. If its password leaks,
the whole account is gone. So it is used for almost nothing:

- turn on **MFA** (multi-factor authentication: a code from a phone app or
  a hardware key, on top of the password) straight away;
- create **no access keys** for it, ever. An access key is a long-lived
  credential for programs; a leaked root key is the worst leak there is;
- lock the credentials away, and do daily work as a less powerful identity.

Exam questions ask about this often: "least privilege" starts with not
using root.

## Users, groups and policies

Three words, and how they fit together:

- An **IAM user** is a long-lived identity in the account: a person who
  signs in to the console with a password, or (less and less often) a
  program using access keys.
- A **group** is a set of users. It cannot sign in; it only collects users
  so that permissions can be given to all of them at once.
- A **policy** is a JSON document listing actions that are allowed or
  denied, such as "may read S3" (written in the next lesson). It does
  nothing until it is **attached** to a user, group or role.

```text
 policy ReadOnlyAccess ──attached to──> group developers
                                          ├── user alice   (gets ReadOnlyAccess)
                                          └── user bob     (gets ReadOnlyAccess)
```

A new user has **no permissions at all**: everything is denied until a
policy allows it. Attach policies to **groups**, not to users: when Alice
changes team, you move her to another group, instead of untangling
permissions one user at a time, and a new hire gets exactly what the team
has by being added to the group. (A policy can also be written straight
into a user, an **inline** policy; the check refuses those as well.)

The commands, one call each:

```
aws iam create-group --group-name developers
aws iam create-user --user-name alice
aws iam add-user-to-group --group-name developers --user-name alice
aws iam attach-group-policy --group-name developers \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
```

`create-group` and `create-user` answer with what they made, including its
ARN; `add-user-to-group` and `attach-group-policy` print nothing when they
succeed:

```
{
    "User": {
        "Path": "/",
        "UserName": "alice",
        "UserId": "0suk0qm91tkkto7h47bj",
        "Arn": "arn:aws:iam::123456789012:user/alice",
        "CreateDate": "2026-11-13T00:25:04.806324Z"
    }
}
```

(The `UserId` is random and differs every time.) `ReadOnlyAccess` is an
**AWS managed policy**: written and kept up to date by AWS, which is why its
ARN has `aws` where an account number would be. **Customer managed
policies**, which you write yourself, carry your account number: next
lesson.

Names have to match exactly. A user who does not exist yet, or a policy name
with a typo, is a `NoSuchEntity` error, which names the thing it could not
find:

```
An error occurred (NoSuchEntity) when calling the AddUserToGroup operation: The user with name zed cannot be found.
An error occurred (NoSuchEntity) when calling the AttachGroupPolicy operation: Policy arn:aws:iam::aws:policy/ReadOnlyAcces was not found.
```

So create things before you refer to them. Creating something twice is
`EntityAlreadyExists`, which is why each Run starts from an empty account.

## Where people really sign in

For an organisation with more than a handful of people, long-lived IAM users
are the old way: every person has another password to manage, and someone
has to remember to delete it when they leave. **IAM Identity Center** gives
people one sign-in (or your existing company directory, connected to AWS)
and hands out short-lived credentials for each account they may use. IAM
users remain for the odd case, and for learning how permissions work, which
is why they are here.

## A password policy

The account's **password policy** applies to every IAM user's console
password: minimum length, which kinds of characters are required, maximum
age, and whether old passwords may be reused. An account has no password
policy until you set one (asking for it before then is a `NoSuchEntity`
error), and setting it replaces the whole policy:

```
aws iam update-account-password-policy --minimum-password-length 14 \
  --require-symbols --require-numbers \
  --require-uppercase-characters --require-lowercase-characters
```

The options without a value are switches: present means "required".

Four facts about password policies that trip people up:

- It applies to IAM users' **console passwords only**: not to the root
  user's password, and not to access keys. A user whose password has
  expired can still use their access keys.
- Without a custom policy, AWS applies a default: at least 8 characters,
  at least three of the four character types, and no expiry. A custom
  policy allows lengths from 6 to 128, expiry after 1 to 1,095 days, and
  preventing reuse of the last 1 to 24 passwords.
- There is no lock-out after failed sign-in attempts, which is one more
  reason every person should also have **MFA**.

## A few more facts about users and groups

- An account can have up to **5,000** IAM users. A user can be in several
  groups (up to 10), or in none, and gets the permissions of all of them.
- Groups **cannot contain other groups**, and a group is not an identity:
  it cannot sign in, and a policy cannot name a group as its `Principal`.
- Each user can have at most **two access keys**. That is so keys can be
  **rotated** without downtime: create the second key, switch every program
  to it, then delete the old one. A leaked key cannot be changed, only
  deleted.
- MFA devices can be an authenticator app on a phone, a security key such
  as a YubiKey, or a hardware token.

## Your task

Fill in `setup.sh` so that it:

1. creates a group **`developers`** with the AWS managed policy
   **`ReadOnlyAccess`** attached;
2. creates users **`alice`** and **`bob`**, both in `developers`, with
   **no policies of their own**: nothing attached to the users, and no inline
   policies;
3. sets the password policy: at least **14** characters, with symbols,
   numbers, upper-case and lower-case letters all required.

Besides reading the settings, the check evaluates Alice's permissions the way
AWS would: through the group alone, she must be able to describe EC2
instances (a read) and must not be able to write to S3.

After **Run**, one call shows the whole picture of who is in what:

```
$ aws iam get-account-authorization-details --query 'UserDetailList[].[UserName,GroupList]'
[
    [
        "alice",
        [
            "developers"
        ]
    ],
    ...
]
```

`aws iam get-account-password-policy` shows the password rules.

## Check yourself

1. Alice moves from development to the data team. What changes, if
   permissions are attached to groups?
   *Only her group membership.*
2. Can you give the `developers` group access in an S3 bucket policy by
   naming the group as the Principal?
   *No: groups cannot be principals. Name the users or, better, a role.*
3. Does the account password policy stop a user whose password expired from
   using their access keys?
   *No. It applies to console passwords only.*
4. Why should the root user have no access keys at all?
   *A leaked root key gives unlimited, unrestrictable access to the whole
   account.*
