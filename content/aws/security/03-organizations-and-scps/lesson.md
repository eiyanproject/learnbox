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

**AWS Organizations** groups accounts into **organizational units** (OUs)
under one **root**, with consolidated billing and central policies. A
multi-account layout is the standard answer to "how do we keep teams,
environments and blast radius apart" - accounts are the strongest isolation
boundary AWS has.

## A common layout

```
Root
├── Security        log archive, security tooling (GuardDuty, Security Hub)
└── Workloads
    ├── Prod        production application accounts
    └── Dev         development and test accounts
```

The **management account** (the one that created the organization) pays the
bill and runs Organizations; keep workloads out of it. **Control Tower**
builds exactly this kind of layout for you, with guardrails and an account
factory.

## Service control policies

An **SCP** sets the **maximum** permissions for every principal in the
accounts below where it is attached - including each account's root user.
It never grants anything: a request must still be allowed by IAM in the
account. AWS evaluates SCPs level by level:

- every level on the path - the root, each OU, the account - must
  **allow** the action (`FullAWSAccess` is attached everywhere by default,
  which is why nothing is blocked until you add denies);
- an explicit **Deny** at any level wins.

So there are two styles: **deny lists** (keep `FullAWSAccess`, add denies -
the usual choice) and **allow lists** (replace `FullAWSAccess` with the
services you allow). SCPs do not affect the management account, or
service-linked roles.

Typical guardrails:

- stop accounts leaving the organization;
- protect the audit trail: deny `cloudtrail:StopLogging`, `DeleteTrail`,
  `UpdateTrail`, and `guardduty:DeleteDetector`;
- restrict Regions with `aws:RequestedRegion` - with `NotAction` for global
  services (IAM, Organizations, STS, Route 53, CloudFront, Support...) whose
  requests go to us-east-1;
- limit cost in development, for example to burstable instance types.

## Tag policies

A **tag policy** standardizes tag keys and values (`CostCenter`, not
`costcenter`), and can enforce them on supported resources. Cost allocation
tags then group the bill.

## Your task

1. An organization with **all features**, SCPs and tag policies enabled.
2. OUs **`Security`** and **`Workloads`** under the root; **`Prod`** and
   **`Dev`** under `Workloads`.
3. Accounts **`log-archive`** (in Security), **`app-prod`** (in Prod) and
   **`app-dev`** (in Dev), with any `@example.com` addresses.
4. An SCP **`baseline-guardrails`** attached to the **root** that denies
   `organizations:LeaveOrganization`, `cloudtrail:StopLogging`,
   `cloudtrail:DeleteTrail`, `cloudtrail:UpdateTrail` and
   `guardduty:DeleteDetector`.
5. An SCP **`region-guard`** attached to **Workloads** that denies every
   action outside **us-east-1** and **eu-west-1**, except the global
   services `iam:*`, `organizations:*`, `sts:*`, `route53:*`,
   `cloudfront:*` and `support:*`.
6. An SCP **`dev-instance-types`** attached to **Dev** that denies launching
   any instance that is not `t3.*` or `t4g.*`.
7. A tag policy **`cost-center`** on the root defining the key
   `CostCenter`.

The checks evaluate the SCPs above each account the way AWS does - for
example, `app-dev` launching an `m5.large` in us-east-1 must be denied,
while `app-prod` may.
