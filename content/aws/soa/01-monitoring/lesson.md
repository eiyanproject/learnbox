---
title: "Domain 1: Monitoring, logging, analysis, remediation and performance"
summary: 22% of the exam. Collecting the right metrics and logs, alarms that mean something, automatic remediation with EventBridge and Systems Manager, and tuning compute, storage and databases.
order: 1
kind: quiz
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **SOA-C03** | the AWS Certified CloudOps Engineer - Associate exam (formerly SysOps Administrator) |
| **qualifier** | the phrase that picks one answer: "LEAST operational overhead", "automatically" |
| **hypervisor** | the layer running instances; EC2's built-in metrics come from it |
| **guest** | the instance's own operating system; EC2 cannot see inside it |
| **CloudWatch agent** | sends memory, disk space, process metrics and log files |
| **Container Insights** | the same for ECS and EKS |
| **evaluation periods** | how many periods an alarm looks at, such as 3 of the last 5 |
| **alarm actions** | SNS, Auto Scaling, EC2 stop/terminate/reboot/recover, Systems Manager |
| **recover** | moves an impaired instance to new hardware, keeping ID, IPs and volumes |
| **`StatusCheckFailed_System`** | the hardware status check that recover acts on |
| **OpsItem** | a Systems Manager work item for an operational issue |
| **composite alarm** | combines alarms with AND and OR to cut noise |
| **dashboard** | a screen of metrics, across accounts and Regions |
| **retention** | log groups keep data for ever unless set |
| **metric filter** / **subscription filter** | pattern to metric (new events only) / stream events to Lambda, Firehose or OpenSearch |
| **Logs Insights** | queries logs |
| **EventBridge** | routes AWS events, CloudTrail API calls and schedules to targets |
| **resource-based permission** | lets `events.amazonaws.com` invoke a Lambda target; the CLI does not add it |
| **Systems Manager Automation** | runbooks for multi-step tasks, such as `AWS-RestartEC2Instance` |
| **runbook** | a documented, runnable procedure |
| **Run Command** | runs a script across many instances, no SSH |
| **Patch Manager** | patches by **patch baseline** in **maintenance windows** |
| **gp2 burst credits** | a small gp2 volume is fast only until its credits run out |
| **Elastic Volumes** | change EBS type or size live |
| **Performance Insights** | shows an RDS database's top SQL and waits |
| **connection storm** | many short connections at once; RDS Proxy pools them |
| **EFS throughput modes** | elastic, provisioned or bursting |
| **placement group**, **Compute Optimizer**, **multipart upload**, **Transfer Acceleration** | performance tools for EC2 and S3 |

---

This page reviews the first domain of the **AWS Certified CloudOps
Engineer - Associate** exam (SOA-C03, formerly SysOps Administrator),
followed by practice questions. This exam is about **running** systems:
seeing what they do, being told when something goes wrong, fixing it,
ideally automatically, and keeping them fast. Each section names the
hands-on lessons where you used what it describes.

**Weight: 22% of the scored questions.**

## How a question is built

As in the other associate exams: a short story, requirements, and a
**qualifier** at the end. In this exam the qualifiers are usually "with the
LEAST operational overhead", "MOST efficient" or "automatically". So
prefer the **managed, automated** option: an alarm action over a person
watching a dashboard, a Systems Manager Automation runbook over a script on
an instance, an EventBridge rule over polling.

## Metrics and logs

*Practised in Operations lessons 1-2.*

- EC2's built-in metrics come from the **hypervisor**: CPU, network, disk
  operations on instance store, status checks. It **cannot see inside the
  guest**, so **memory**, **disk space** and **processes** need the
  **CloudWatch agent** on the instance (it also sends log files, from EC2
  and on-premises servers). **Container Insights** does the same for ECS and
  EKS.
- **Alarms** compare a metric to a threshold over **evaluation periods**
  ("3 of the last 5 minutes"), with three states (`OK`, `ALARM`,
  `INSUFFICIENT_DATA`). Their **actions**:

  | Action | For |
  |---|---|
  | SNS | notify people or systems |
  | Auto Scaling | add or remove capacity |
  | EC2: stop, terminate, reboot, **recover** | recover moves an impaired instance to new hardware, keeping its ID, IPs and EBS volumes (on `StatusCheckFailed_System`) |
  | Systems Manager | run an Automation runbook or open an OpsItem |

  **Composite alarms** combine alarms with AND and OR, so a page fires only
  when several things are wrong together: less noise.
- **Dashboards** can show metrics from several accounts and Regions on one
  screen.
- **Logs**: set **retention** (the default is to keep for ever, and pay for
  ever); **metric filters** turn patterns into metrics (new events only);
  **subscription filters** stream log events to Lambda, Firehose or
  OpenSearch as they arrive; **Logs Insights** queries logs with a small
  query language.

## Reacting automatically

*Practised in Serverless lesson 4, Operations lesson 2.*

- **EventBridge** routes **events** to targets by rule: AWS service events
  (an instance stopped, a GuardDuty finding, a Config compliance change),
  **CloudTrail API calls** (someone called `AuthorizeSecurityGroupIngress`),
  and **schedules**. ❗ A Lambda target needs a **resource-based
  permission** allowing `events.amazonaws.com` to invoke it; the console
  adds it, the CLI does not.
- **Systems Manager** does the routine work on fleets:

  | Feature | Does |
  |---|---|
  | **Automation** runbooks | multi-step operational tasks: AWS-provided (`AWS-RestartEC2Instance`, `AWS-StopEC2Instance`...) or your own |
  | **Run Command** | runs a command or script across many instances at once, with no SSH |
  | **Patch Manager** | patches instances by **patch baseline**, in **maintenance windows** |

  Typical chain: an alarm or an EventBridge rule starts an Automation
  runbook, which fixes the problem without a person.

| In a question | Answer |
|---|---|
| "monitor memory or disk space on EC2" | the CloudWatch agent |
| "page only when both latency and errors are high" | a composite alarm |
| "the instance's hardware failed; keep its IP" | alarm on `StatusCheckFailed_System` with the recover action |
| "react when someone opens a security group to the world" | EventBridge rule on the CloudTrail event, then Lambda or Automation |
| "patch all instances every Sunday night" | Patch Manager with a maintenance window |
| "stream logs to OpenSearch in near real time" | a subscription filter |

## Performance

- **EBS**: **gp3** sets IOPS and throughput independently of size, where
  **gp2** ties them to size and uses burst credits (a small gp2 volume is
  fast only until its credits run out). Change type or size live with
  **Elastic Volumes**. **io2** for the highest consistent IOPS.
- **RDS**: **Performance Insights** shows the top SQL statements and what
  the database waits on; **RDS Proxy** pools connections for connection
  storms (many short Lambda connections); read replicas for read load.
- **EFS**: throughput modes (**elastic**, provisioned, bursting) and
  lifecycle management to cheaper tiers.
- **EC2**: **placement groups** (cluster for low latency between
  instances); instance types matched to the bottleneck (Compute Optimizer
  recommends).
- **S3**: **multipart upload** for large objects, **Transfer Acceleration**
  for distant clients, more prefixes for very high request rates.

| In a question | Answer |
|---|---|
| "database is slow; find which queries" | RDS Performance Insights |
| "gp2 volume slows down after a while" | burst credits exhausted: gp3 with provisioned IOPS |
| "too many database connections from Lambda" | RDS Proxy |

## Traps

- No agent, no memory metric.
- **Metric filters** are not retroactive.
- The **recover** action is for system (hardware) status check failures,
  not for problems inside the operating system (reboot for those).
- Log groups keep data **for ever** unless retention is set.

Source: AWS Certified CloudOps Engineer - Associate (SOA-C03) exam guide,
Content Domain 1; AWS service documentation.

## Questions from open banks

- 65 questions by **zghanw** from github.com/zghanw/aws-cloudops-engineer-associate (commit c2e7acc), MIT licence. Their ids start with `zg-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
