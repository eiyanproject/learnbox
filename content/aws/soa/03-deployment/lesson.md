---
title: "Domain 3: Deployment, provisioning and automation"
summary: 22% of the exam. Golden images, CloudFormation and the CDK, deploying across accounts and Regions, fixing stacks that fail, and Systems Manager doing the routine work.
order: 3
kind: quiz
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **golden image** | an AMI with the OS patched and software installed |
| **EC2 Image Builder** | pipelines that build, test and distribute images on a schedule |
| **bootstrapping** | an instance setting itself up at first boot |
| **change set** | previews an update, including replacements |
| **drift detection** | finds hand changes; does not undo them |
| **`DeletionPolicy`** | `Retain` or `Snapshot` when the stack is deleted |
| **`CreationPolicy`** + **`cfn-signal`** | the stack waits for the instance to report success |
| **`UPDATE_ROLLBACK_FAILED`** | an update and its rollback both failed; fix, then continue update rollback |
| **continue update rollback** | retries the rollback, optionally skipping broken resources |
| **CDK** / **synthesize** | infrastructure in a programming language / produce the CloudFormation template |
| **StackSets** | one template to many accounts and Regions, automatically for new accounts in an OU |
| **service-managed permissions** | StackSets using Organizations to deploy |
| **AWS RAM** | Resource Access Manager: shares subnets, Transit Gateways and more between accounts |
| **`iam:PassRole`** | permission to hand a role to a service; separate from creating the resource |
| **service quota** | a limit; request an increase when "limit exceeded" |
| **State Manager** | keeps a configuration applied on a schedule |
| **Session Manager** | logged shell access through IAM, no bastion or open port |
| **managed instance** | appears in Systems Manager: needs the SSM Agent, a profile with `AmazonSSMManagedInstanceCore`, and a network path |
| **SSM Agent** | the Systems Manager software on the instance |
| **event-driven automation** | rules and notifications start the work, not a person |

### Errors

| Error | Means |
|---|---|
| "insufficient IP addresses" | the subnet is too small |
| `AccessDenied` creating or passing a role | often missing `iam:PassRole` |
| "limit exceeded" | a service quota was reached |

---

Every server, stack and setting should come from something repeatable: a
**golden image**, a **template**, a **runbook**, never hand-made steps that
nobody can redo. This domain covers building those, deploying them across
accounts and Regions, fixing deployments that fail, and letting Systems
Manager do the routine work.

**Weight: 22% of the scored questions.**

## Images

- A **golden image** is an AMI with the operating system patched and the
  software installed, so instances start ready instead of installing
  everything at boot. **EC2 Image Builder** pipelines build, test and
  distribute AMIs and container images on a **schedule**, so patched images
  appear by themselves; Auto Scaling **instance refresh** then rolls them
  out.

## CloudFormation and the CDK

*Practised in Operations lesson 3.*

- **Change sets** show what an update will add, modify or **replace** before
  it runs.
- **Drift detection** finds resources changed by hand outside the stack.
- **`DeletionPolicy`**: `Retain` keeps the resource when the stack is
  deleted, `Snapshot` takes a final snapshot (databases, volumes).
- **`CreationPolicy`** with **`cfn-signal`**: the stack waits until the
  instance reports that its bootstrapping succeeded, and fails (and rolls
  back) if no signal arrives in time. Without it, a stack is "complete"
  while the software is still installing, or failed.
- **`UPDATE_ROLLBACK_FAILED`**: an update failed, and so did the rollback
  (often because a resource was changed or deleted by hand). Fix the cause,
  then **continue update rollback**, optionally skipping the broken
  resources.
- The **CDK** writes infrastructure in a programming language and
  **synthesizes** a CloudFormation template; deployment is still
  CloudFormation.

## Many accounts and Regions

- **StackSets** deploy one template to many accounts and Regions. With
  Organizations (service-managed permissions), they deploy automatically to
  **new accounts** added to a target OU.
- **AWS RAM** (Resource Access Manager) **shares** resources between
  accounts instead of duplicating them: VPC **subnets**, Transit Gateways,
  Route 53 Resolver rules, License Manager configurations.

## When a deployment fails

| Symptom | Usual cause |
|---|---|
| "insufficient IP addresses" | the subnet is too small for the instances, tasks or Lambda interfaces |
| `AccessDenied` creating or passing a role | missing permissions, often **`iam:PassRole`** (needed to hand a role to EC2, Lambda, ECS, CloudFormation) |
| "limit exceeded" | a **service quota**: request an increase |
| stack waits, then fails on an instance | no `cfn-signal` arrived: the user data script failed |

## Systems Manager

*Practised in Foundations lesson 8.*

| Feature | Does |
|---|---|
| **Run Command** | runs scripts across a fleet at once, no SSH |
| **State Manager** | keeps a configuration applied, re-applying it on a schedule |
| **Session Manager** | shell access through IAM, logged, with **no bastion and no open port** |
| **Parameter Store** | configuration and secrets |
| **Automation** | runbooks for multi-step tasks |
| **Patch Manager** | patching by baseline in maintenance windows |

❗ An instance appears as **managed** only with all three: the **SSM
Agent** running (preinstalled on Amazon Linux and recent Windows AMIs), an
**instance profile** with `AmazonSSMManagedInstanceCore`, and a network
path to the Systems Manager endpoints (internet through NAT, or the `ssm`,
`ssmmessages` and `ec2messages` interface endpoints).

**Event-driven automation**: EventBridge rules and schedules, S3 event
notifications and Lambda start the work when something happens, rather
than a person or a polling script.

| In a question | Answer |
|---|---|
| "monthly patched AMIs, automatically" | EC2 Image Builder |
| "the stack reports success before the app is installed" | `CreationPolicy` + `cfn-signal` |
| "the database must survive deleting the stack" | `DeletionPolicy: Retain` (or `Snapshot`) |
| "same baseline stack in every new account" | StackSets with Organizations |
| "share one VPC's subnets with other accounts" | AWS RAM |
| "the instance does not appear in Systems Manager" | agent, instance profile, or network path missing |

## Traps

- An update stuck in **`UPDATE_ROLLBACK_FAILED`** needs **continue update
  rollback**, not deleting the stack.
- **Drift detection** reports changes; it does not undo them.
- `iam:PassRole` is separate from creating the resource.

Source: AWS Certified CloudOps Engineer - Associate (SOA-C03) exam guide,
Content Domain 3; AWS service documentation.

## Questions from open banks

- 65 questions by **zghanw** from github.com/zghanw/aws-cloudops-engineer-associate (commit c2e7acc), MIT licence. Their ids start with `zg-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
