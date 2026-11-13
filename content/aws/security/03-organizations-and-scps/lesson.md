---
title: Organizations and service control policies
summary: An organization with OUs for security and workloads, member accounts placed in them, guardrail SCPs at the root, a Region restriction on workloads, an instance-type limit on development, and a tag policy - checked by evaluating the SCPs as AWS does.
order: 3
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`aws organizations create-organization --feature-set ALL`, then `ROOT=$(aws organizations list-roots --query 'Roots[0].Id' --output text)` and `aws organizations enable-policy-type --root-id \"$ROOT\" --policy-type SERVICE_CONTROL_POLICY` (and TAG_POLICY)."
  - "`aws organizations create-organizational-unit --parent-id \"$ROOT\" --name Workloads --query OrganizationalUnit.Id --output text`; for Prod and Dev the parent is the Workloads OU."
  - "Creating an account is asynchronous: `aws organizations create-account --email app-prod@example.com --account-name app-prod --query CreateAccountStatus.Id --output text`, then `describe-create-account-status` until it SUCCEEDED, and read `.AccountId`. Every new account starts under the root; `move-account` puts it in its OU."
  - "The Region guard is a Deny with `NotAction` for the global services and `\"Condition\": {\"StringNotEquals\": {\"aws:RequestedRegion\": [\"us-east-1\", \"eu-west-1\"]}}`."
  - "The instance-type guard: `\"Action\": \"ec2:RunInstances\"`, `\"Resource\": \"arn:aws:ec2:*:*:instance/*\"`, `\"Condition\": {\"StringNotLike\": {\"ec2:InstanceType\": [\"t3.*\", \"t4g.*\"]}}`. Scope the Resource to instances: RunInstances is also authorized on subnets, volumes and network interfaces, which have no instance type."
---

Everything so far happened in one account. Real companies use many: one
per team, per environment, per product. An **AWS account** is the strongest
isolation boundary AWS has: nothing in one account can touch another unless
someone explicitly allows it, so a mistake or a breach in the development
account cannot spread to production. But many accounts raise new questions:
who pays, how do you stop each account's administrators from switching off
the audit trail, and how do you make sure development cannot launch
expensive machines?

**AWS Organizations** answers them. It groups accounts under one **root**,
in **organizational units** (OUs, folders of accounts that can contain other
OUs), with one bill and central policies.

## A common layout

```text
 Root                         (the organization's top; policies here reach every account)
 ├── Security                 log archive, security tooling (GuardDuty, Security Hub)
 │   └── log-archive
 └── Workloads
     ├── Prod                 production application accounts
     │   └── app-prod
     └── Dev                  development and test accounts
         └── app-dev
```

The **management account** is the account that created the organization.
It pays the bill and runs Organizations; keep workloads out of it, because,
as below, the organization's policies do not apply to it. Every other account
is a **member account**, and an account belongs to one organization at a
time. Accounts are created from inside the organization (`create-account`,
needing only a unique email address) or invited to join.

What the organization gives:

- **Consolidated billing**: one payment method for every account, and
  usage added up across accounts for volume discounts, with Reserved
  Instances and Savings Plans shared among them.
- **Central control**: policies attached to the root, an OU or an account
  apply to everything below.
- **Central services**: an organization trail for CloudTrail (Operations
  lesson 2), shared security tooling, and IAM Identity Center for signing
  in to every account.

**Control Tower** builds exactly this kind of layout for you: a **landing
zone** with the Security OU's log archive and audit accounts, Identity
Center, an **account factory** for creating standardized accounts, and
**guardrails**, which are either **preventive** (SCPs that stop an action) or
**detective** (Config rules that report one).

## Service control policies

A **service control policy** (SCP) sets the **maximum** permissions for
every principal in the accounts below where it is attached, **including each
account's root user**. It looks like an IAM policy, but it **never grants**
anything: a request must still be allowed by the account's own IAM
policies. It is a ceiling, like a permissions boundary for whole accounts.

AWS evaluates SCPs level by level, along the path from the root to the
account:

- **every** level on the path, the root, each OU and the account itself,
  must **allow** the action;
- an explicit **Deny** at **any** level wins, and is inherited by everything
  below.

By default every root, OU and account has the AWS managed SCP
**`FullAWSAccess`** attached, which allows everything; that is why nothing is
blocked until you add denies. ❗ Detaching `FullAWSAccess` without a
replacement blocks **every** action in that part of the organization.

A worked example:

| Where | SCPs attached | Allowed there |
|---|---|---|
| Sandbox OU | FullAWSAccess, deny S3 | everything except S3 |
| account A, in Sandbox | FullAWSAccess, deny EC2 | everything except S3 and EC2 (it inherits the S3 deny) |
| account B, in Sandbox | FullAWSAccess | everything except S3 |
| account C, in an OU that has only "allow EC2" | FullAWSAccess | **only EC2**: the OU level allows nothing else |
| the management account | anything | **everything**: SCPs never apply to it |

So there are two styles: **deny lists** (keep `FullAWSAccess` everywhere, add
denies: the usual choice, used here) and **allow lists** (replace
`FullAWSAccess` with the services you permit: tighter, and more work). SCPs
also do not restrict **service-linked roles**, which AWS services use to act
for you.

### Typical guardrails

- Stop accounts **leaving** the organization (and so escaping its
  policies): deny `organizations:LeaveOrganization`.
- Protect the **audit trail**: deny `cloudtrail:StopLogging`,
  `cloudtrail:DeleteTrail`, `cloudtrail:UpdateTrail`, and
  `guardduty:DeleteDetector`. An intruder with an account's administrator
  rights can then still not hide their tracks.
- **Restrict Regions** with the condition key `aws:RequestedRegion`, the
  Region a request is sent to.
- **Limit cost** in development, for example to small, burstable instance
  types.

### The Region guard, and NotAction

Some services are **global**: IAM, Organizations, STS, Route 53, CloudFront
and Support have no Regions, and their requests are handled in us-east-1.
Here us-east-1 is one of the allowed Regions, so they would happen to work,
but an organization that allows only, say, eu-west-1 would lock everyone out
of IAM. The standard pattern, which the check requires, exempts them with
**`NotAction`**, meaning "every action **except** these":

```json
{
  "Effect": "Deny",
  "NotAction": ["iam:*", "organizations:*", "sts:*", "route53:*", "cloudfront:*", "support:*"],
  "Resource": "*",
  "Condition": {"StringNotEquals": {"aws:RequestedRegion": ["us-east-1", "eu-west-1"]}}
}
```

Read it as "deny every action except the global services' ones, when the
request goes to a Region other than us-east-1 or eu-west-1". A condition
whose value is a list matches if **any** item matches, so `StringNotEquals`
with two Regions is "neither of these".

### The instance-type guard, and resource scoping

Launching an instance is one action, `ec2:RunInstances`, but it is
authorized against **several** resources at once: the instance, and the
subnet, network interface, volumes and image it uses. Only the instance has
an `ec2:InstanceType`. So the deny must name only instances in its
`Resource`, `arn:aws:ec2:*:*:instance/*`; with `"Resource": "*"`, the
check of the subnet, which has no instance type, would also match
`StringNotLike` and deny every launch, even of a `t3.micro`. The check tests
exactly that. `StringNotLike` compares with wildcards: `t3.*` matches any
size of `t3`.

## Tag policies

A **tag policy** standardizes tag keys and values across accounts:
`CostCenter`, not `costcenter` or `cost-center`. It can report non-compliant
resources, and enforce the spelling on supported resource types. Cost
allocation tags then split the bill by cost centre. Its content uses its own
small language, with `@@assign` setting a value:

```json
{"tags": {"CostCenter": {"tag_key": {"@@assign": "CostCenter"}}}}
```

## Working with the API

Each part has a create call that returns an ID to capture: the root (`r-...`,
from `list-roots`), OUs (`ou-...`), accounts (12 digits), policies (`p-...`).
Two things are less obvious:

- Policy types must be **enabled** on the root before policies of that type
  can be attached: `enable-policy-type --policy-type SERVICE_CONTROL_POLICY`
  (and `TAG_POLICY`). The organization needs the **all features** set, not
  just consolidated billing.
- **Creating an account is asynchronous**. `create-account` returns a
  request ID straight away; poll `describe-create-account-status` until its
  `State` is `SUCCEEDED` (or `FAILED`), then read the `AccountId`. Every new
  account starts directly under the root, and `move-account` (with the
  source and destination parent IDs) puts it in its OU. A shell loop does
  the polling:

  ```bash
  for _ in $(seq 30); do
    state=$(aws organizations describe-create-account-status \
      --create-account-request-id "$req" --query CreateAccountStatus.State --output text)
    [ "$state" = SUCCEEDED ] && break
    sleep 2
  done
  ```

The same steps for three accounts, or four SCPs, are a natural use for small
shell functions.

## Your task

1. An organization with **all features**, and both SCPs and tag policies
   enabled on its root.
2. OUs **`Security`** and **`Workloads`** under the root; **`Prod`** and
   **`Dev`** under `Workloads`.
3. Accounts **`log-archive`** (in Security), **`app-prod`** (in Prod) and
   **`app-dev`** (in Dev), with any `@example.com` addresses.
4. An SCP **`baseline-guardrails`** attached to the **root** that denies
   `organizations:LeaveOrganization`, `cloudtrail:StopLogging`,
   `cloudtrail:DeleteTrail`, `cloudtrail:UpdateTrail` and
   `guardduty:DeleteDetector`.
5. An SCP **`region-guard`** attached to **Workloads** only that denies
   every action outside **us-east-1** and **eu-west-1**, except the global
   services `iam:*`, `organizations:*`, `sts:*`, `route53:*`,
   `cloudfront:*` and `support:*`.
6. An SCP **`dev-instance-types`** attached to **Dev** only that denies
   launching any instance that is not `t3.*` or `t4g.*`, scoped to instance
   resources.
7. A tag policy **`cost-center`** attached to the root, defining the key
   `CostCenter`.

Leave `FullAWSAccess` attached everywhere: these are deny lists. The checks
evaluate the SCPs above each account the way AWS does:

| Request | Account | Should be |
|---|---|---|
| any of the baseline actions | every account | denied |
| `s3:PutObject` in us-east-1 | every account | allowed |
| `ec2:RunInstances` in ap-south-1 | app-prod | denied |
| `ec2:RunInstances` in eu-west-1 | app-prod | allowed |
| `iam:` and other global actions, from any Region | app-prod | allowed |
| `s3:PutObject` in ap-south-1 | log-archive | allowed (the Region guard is on Workloads only) |
| an `m5.large` | app-dev | denied |
| a `t3.micro` or `t4g.small` | app-dev | allowed |
| an `m5.large` | app-prod | allowed |

After **Run**, `aws organizations list-accounts --query
'Accounts[].[Name,Status]' --output text` lists the accounts (the emulator's
management account is called `master`), and `aws organizations
list-policies --filter SERVICE_CONTROL_POLICY --query 'Policies[].Name'`
the SCPs, `FullAWSAccess` among them.

## Check yourself

1. Does an SCP that allows `s3:*` let users in the account use S3?
   *Only if their own IAM policies allow it too; SCPs never grant.*
2. An account's administrator tries to stop the CloudTrail trail. What
   happens, with `baseline-guardrails` attached to the root?
   *Denied, even for the account's root user.*
3. Why keep workloads out of the management account?
   *SCPs do not apply to it, so none of the guardrails would protect them.*
4. Why does `dev-instance-types` name `instance/*` as its Resource?
   *`RunInstances` is also checked against subnets and other resources,
   which have no instance type; with `*`, every launch would be denied.*
5. What happens if `FullAWSAccess` is detached from an OU and nothing
   replaces it?
   *Every action in the accounts below is denied.*
