---
title: "Domain 5: Incident and event response"
summary: 14% of the exam. Manage event sources, act on events automatically, and troubleshoot failed deployments, scaling and services.
order: 5
kind: quiz
---

An **event** is something that happened: an instance stopped, a deployment
failed, a finding appeared, AWS scheduled maintenance. An **incident** is
when that hurts users. This domain covers routing events to automated
responses, organizing the human response when one is needed, and reading
the right signal to find out why a deployment, scaling or service failed.
The method for reading questions is on the Domain 1 page.

**Weight: 14% of the scored questions.**

## Event sources and routing

*Practised in Serverless lesson 4, Operations lesson 2.*

- **EventBridge** rules match events from AWS services: EC2 state changes,
  **AWS Health**, CodePipeline and CodeDeploy state changes, GuardDuty
  findings, Config compliance changes, and CloudTrail API calls. Event
  buses can send events **across accounts** to a central bus. **Input
  transformers** reshape the event for the target. **Archive and replay**
  keeps events and sends them again, for example after fixing a broken
  consumer.
- **AWS Health** reports scheduled maintenance (an instance retirement) and
  service issues affecting **your** resources; the **organizational view**
  shows them for every account.
- **S3 event notifications** and **SNS fan-out**.

## Automated response

- **EventBridge** to Lambda, Step Functions, **Systems Manager Automation**
  runbooks or SNS. Example: an AWS Health event for an instance retirement
  starts a runbook that stops and starts the instance on new hardware in the
  maintenance window.
- **Config auto-remediation**; **Auto Scaling** replacing unhealthy
  instances.
- **Systems Manager Incident Manager**: **response plans** that engage the
  right people, **escalation** when nobody answers, runbooks, and a
  timeline for the post-incident review. **OpsCenter** collects
  **OpsItems**: operational issues to investigate, with related resources
  and runbooks.

## Troubleshooting: read the right signal

| Failed | Look at |
|---|---|
| a CodeDeploy deployment | the deployment's **lifecycle event** that failed, and the agent's logs on the instance |
| a CloudFormation stack | the stack **events**: the **first** `CREATE_FAILED`; later failures are usually consequences |
| an Auto Scaling launch | the group's **activity history** (quota, capacity, launch template errors) |
| an ECS task | the **stopped reason** of the task (`CannotPullContainerError`, essential container exited, health checks) |
| a Lambda function | `Throttles`, `Errors`, the DLQ or failure destination, the logs |
| anything "limit exceeded" | **Service Quotas** |

| In a question | Answer |
|---|---|
| "notify the team of AWS maintenance for our instances" | an EventBridge rule on AWS Health events |
| "events from 50 accounts in one place" | cross-account event buses to a central bus |
| "reprocess last week's events after fixing the consumer" | EventBridge archive and replay |
| "page the on-call engineer and escalate" | Incident Manager response plans |
| "why did the stack fail?" | the first failure in the stack events |

## Traps

- In stack events, the **first** failure is the cause.
- AWS Health covers **your** affected resources; the Service Health
  Dashboard is the public view.
- An EventBridge rule with a Lambda target needs the function's resource
  policy to allow `events.amazonaws.com`.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 5; AWS service documentation.

## Questions from open banks

- 2 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
