---
title: Writing IAM policies
summary: The JSON behind every permission - Effect, Action, Resource - how AWS decides between allow and deny, and a least-privilege policy of your own.
order: 3
files: [setup.sh, policy.json]
run: awslab run setup.sh
hints:
  - "Listing a bucket and reading its objects are two different resources. `s3:ListBucket` acts on the bucket, `arn:aws:s3:::lb-reports`; `s3:GetObject` acts on objects, `arn:aws:s3:::lb-reports/*`. One statement each."
  - "An explicit Deny beats any Allow. A third statement with `\"Effect\": \"Deny\"`, `\"Action\": \"s3:GetObject\"` and `\"Resource\": \"arn:aws:s3:::lb-reports/private/*\"` keeps private/ out of reach even though the second statement allows everything in the bucket."
  - "`aws iam create-policy --policy-name reports-read --policy-document file://policy.json` - note the `file://`. The command prints the new policy's ARN, `arn:aws:iam::123456789012:policy/reports-read`."
  - "No `*` for actions or resources: the check reads the document and refuses `\"Action\": \"s3:*\"` or `\"Resource\": \"*\"` in an Allow."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **policy document** | the JSON text of a policy: a version and a list of statements |
| **statement** | one rule in a policy: an effect, actions and resources |
| **`Version`** | the policy language version, always `2012-10-17` |
| **`Effect`** | `Allow` or `Deny` |
| **`Action`** | `service:Operation`, such as `s3:GetObject`, or a list of them |
| **`Resource`** | the ARN (or ARNs) a statement applies to |
| **`Sid`** | statement ID: an optional label |
| **`Condition`** | narrows a statement further, such as "only with MFA" |
| **wildcard** | `*` matches any run of characters, `?` any one: `s3:Get*` |
| **bucket ARN** vs **object ARN** | `arn:aws:s3:::bucket` vs `arn:aws:s3:::bucket/key`; S3 ARNs have no Region or account |
| **key** | an object's full name inside a bucket |
| **explicit deny** | a matching `Deny` statement; always wins |
| **implicit deny** | the refusal when nothing allows the request |
| **least privilege** | grant exactly what the job needs and no more |
| **customer managed policy** | one you create; its ARN carries your account number |
| **shell variable** | a named value in the shell, used as `"$POLICY_ARN"` |
| **identity-based policy** | attached to a user, group or role: what it may do |
| **resource-based policy** | attached to a resource, with a `Principal`: who may use it (bucket, queue, key policies) |
| **trust policy** | on a role: who may assume it |
| **permissions boundary** | the most a user or role can ever be given |
| **service control policy (SCP)** | the most anyone in an Organization's accounts can do |
| **session policy** | narrows one assumed-role session |
| **cap** | limit what other policies grant, without granting anything |
| **cross-account** | a request from one account to a resource in another; both sides must allow it |
| **IAM policy simulator** | answers "would this be allowed?" without making the request |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `aws iam create-policy --policy-name N --policy-document file://policy.json` | creates a customer managed policy from a file |
| `file://policy.json` | read the option's value from that file |
| `VAR=$(command)` | stores what the command printed in a shell variable |
| `--query Policy.Arn --output text` | picks just the new policy's ARN |
| `aws iam list-policies --scope Local` | lists your own policies |
| `aws iam get-policy-version --policy-arn ARN --version-id v1` | prints the stored policy document |
| `aws iam simulate-principal-policy --policy-source-arn ARN --action-names A` | the policy simulator (not in the emulator) |
| `s3:ListBucket` | lists a bucket; acts on the bucket ARN |
| `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` | read, write, delete an object; act on object ARNs |

### Errors

| Error | Means |
|---|---|
| `MalformedPolicyDocument ... Syntax errors in policy` | broken JSON, or `file://` left out so the file name itself was sent |
| `MalformedPolicyDocument ... Policy statement must contain resources` | a statement with no `Resource` |
| `AccessDenied` | the request was refused; it does not say which ARN was wrong |

---

Last lesson used a ready-made policy, `ReadOnlyAccess`, which can read
everything in the account. Real teams need something narrower: "these people
may read these reports, but not the salary files, and may change nothing".
That means writing a policy yourself. Every permission in AWS, whoever wrote
it, is a **policy document**: a piece of JSON with a list of **statements**.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadReports",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::lb-reports/*"
    }
  ]
}
```

Read it as a sentence: "**allow** the action **s3:GetObject** (reading an
object) on the **resources** `arn:aws:s3:::lb-reports/*` (every object in
the bucket `lb-reports`)". The parts:

- **Version** is always `2012-10-17`: the version of the policy language,
  not a date you choose. Leave it out and some features silently stop
  working.
- **Effect** is `Allow` or `Deny`.
- **Action** is `service:Operation`, or a list of them. `*` matches any
  run of characters and `?` any one, so `s3:Get*` is every S3 action that
  starts with `Get`.
- **Resource** is one ARN, or a list of them, that the statement applies
  to. S3 ARNs have no Region or account, because bucket names are global:
  `arn:aws:s3:::bucket` for the bucket, `arn:aws:s3:::bucket/key` for an
  object.
- **Sid** (statement ID) is an optional label, useful in error messages and
  reviews. **Condition**, in later lessons, narrows a statement further:
  only from this network, only with MFA, only over encrypted connections.

## How AWS decides

Every request, such as "carol wants `s3:GetObject` on
`lb-reports/q1.csv`", is checked against **every** policy that applies to
the person making it: those attached to them, and to their groups. AWS
evaluates in this order:

```text
 Does any statement that matches the request say Deny?
     yes ──> DENIED   (an explicit deny always wins)
     no
 Does any statement that matches the request say Allow?
     yes ──> ALLOWED
     no  ──> DENIED   (the implicit deny: nothing allowed it)
```

Two consequences follow:

- Permissions only ever **add up from nothing**. A new user can do nothing;
  each Allow adds something.
- A **Deny** is how to carve an exception out of a broad Allow, and nothing
  can override it: not another Allow, not a second policy, not being an
  administrator.

## Buckets are not objects

This is the classic trap. In S3, the bucket and the objects in it are
different resources, with different ARNs, and each action acts on one kind
or the other:

| Action | Acts on | Resource ARN |
|---|---|---|
| `s3:ListBucket` | the bucket (listing what is in it) | `arn:aws:s3:::lb-reports` |
| `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` | objects | `arn:aws:s3:::lb-reports/*` |

A policy allowing `s3:ListBucket` on `arn:aws:s3:::lb-reports/*` allows
nothing at all: the statement names objects, and listing is not something
you do to an object. In a real account, the request is simply refused with
`AccessDenied`, and the error does **not** tell you which ARN was wrong. So
the bucket and its objects get one statement each.

## Least privilege

**Least privilege** means granting exactly what the job needs and no more.
`"Action": "s3:*"` with `"Resource": "*"` works on day one, and on day two
becomes the reason a compromised laptop could delete every bucket in the
account. Start narrow, naming the actions and the resources, and widen when
something real needs it.

## Creating the policy

A policy you write is created with `create-policy`, reading the JSON from a
file:

```
POLICY_ARN=$(aws iam create-policy --policy-name reports-read \
  --policy-document file://policy.json \
  --query Policy.Arn --output text)
```

Three details:

- **`file://`** tells the CLI to read the option's value from that file.
  Without it, the CLI sends the text `policy.json` itself as the policy,
  and IAM answers
  `An error occurred (MalformedPolicyDocument) when calling the CreatePolicy operation: Syntax errors in policy.`
  The same error comes back for broken JSON, such as a comma before a `}`.
- `create-policy` answers with the new policy, including its ARN,
  `arn:aws:iam::123456789012:policy/reports-read` (a customer managed
  policy carries your account number). `--query Policy.Arn --output text`
  picks out just the ARN.
- `VARIABLE=$( ... )` runs the command and stores what it printed in a
  shell variable, so the next command can use it as `"$POLICY_ARN"`. This is
  how values travel between the steps of every later lesson.

IAM checks the document's structure when you create it. A statement with no
`Resource`, for example, is refused:
`MalformedPolicyDocument ... Policy statement must contain resources.` It
does not check whether the policy does what you *meant*; that is what the
check below is for.

## The kinds of policy

This lesson writes an **identity-based** policy: attached to a user, group
or role, saying what that identity may do. It is one of several kinds, and
later lessons meet the rest:

| Kind | Attached to | Says |
|---|---|---|
| **Identity-based** (AWS managed, customer managed, inline) | users, groups, roles | what this identity can do |
| **Resource-based** (bucket policies, queue policies, key policies) | a resource; has a `Principal` | who can use this resource, including other accounts |
| **Trust policy** | a role | who may assume the role (lesson 4) |
| **Permissions boundary** | a user or role | the most it can ever be given |
| **Service control policy** | accounts and OUs in an Organization | the most anyone in those accounts can do (section 7) |
| **Session policy** | one assumed-role session | narrows that session further |

Boundaries, SCPs and session policies never grant anything; they only cap.
Within one account, an Allow in **either** the identity's policies **or** the
resource's policy is usually enough. Across accounts, **both** sides must
allow it: the caller's identity policy, and the resource policy in the
other account.

In a real account, the **IAM policy simulator** answers "would this request
be allowed?" without making it: `aws iam simulate-principal-policy
--policy-source-arn <user ARN> --action-names s3:GetObject`. (The emulator
does not offer it; this lesson's check does the same evaluation itself.)

## Your task

The analysts need to read reports from the bucket `lb-reports`, but not the
files under `private/`, and they must not be able to change anything.

1. Write **`policy.json`** with three statements: allow **listing** the
   bucket `lb-reports`, allow **reading** every object in it, and
   **explicitly deny** reading anything under `private/`.
2. In `setup.sh` (which already creates the bucket), create it as a customer
   managed policy named **`reports-read`**, create a group **`analysts`**
   with it attached, and a user **`carol`** in that group, and in no other
   group.

No `*` wildcards in the actions or resources of an Allow statement:
`lb-reports/*` is fine, since it names one bucket's objects, but
`"Action": "s3:*"` and `"Resource": "*"` are refused.

The check reads your policy the way AWS would and asks four questions:

| carol asks for | on | should be |
|---|---|---|
| `s3:ListBucket` | `arn:aws:s3:::lb-reports` | allowed |
| `s3:GetObject` | `arn:aws:s3:::lb-reports/q1.csv` | allowed |
| `s3:GetObject` | `arn:aws:s3:::lb-reports/private/salaries.csv` | **explicitly** denied (by your Deny, not just because nothing allows it) |
| `s3:PutObject`, `s3:DeleteObject` | `arn:aws:s3:::lb-reports/q1.csv` | denied |

After **Run**, `aws iam list-policies --scope Local` lists your own
policies, and `aws iam get-policy-version --policy-arn "<the ARN>"
--version-id v1` prints the document as IAM stored it.

## Check yourself

1. A policy allows `s3:ListBucket` on `arn:aws:s3:::lb-reports/*`. Can the
   user list the bucket?
   *No: listing acts on the bucket, `arn:aws:s3:::lb-reports`, with no
   `/*`.*
2. One policy allows `s3:*` on a bucket, another denies `s3:DeleteObject`
   on it. Can the user delete an object?
   *No: an explicit deny always wins.*
3. A user has no policies at all. What can they do?
   *Nothing: everything not allowed is implicitly denied.*
4. Why is `"Action": "s3:*", "Resource": "*"` a bad idea even if it works?
   *It grants far more than the job needs, including deleting every bucket
   in the account.*
