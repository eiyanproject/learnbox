---
title: "Domain 4: Monitoring and logging"
summary: 15% of the exam. Collect, aggregate and store logs and metrics, audit and analyse them, and automate monitoring across accounts.
order: 4
kind: quiz
---

You cannot automate a response to what you cannot see. This domain covers
collecting logs and metrics from everything, keeping them centrally and
safely, analysing them, and setting up monitoring itself as code across
many accounts. The method for reading questions is on the Domain 1 page.

**Weight: 15% of the scored questions.**

## Collect and store

*Practised in Operations lessons 1-2.*

- The **CloudWatch agent** collects memory, disk and custom log files from
  instances; keep its configuration in **Parameter Store**, so every
  instance loads the same one.
- **Custom metrics** with `PutMetricData` or the **embedded metric format**
  (metrics written as structured log lines); **high-resolution** metrics
  down to 1 second.
- **Log groups** with **retention** set, and **KMS encryption** with your
  key.
- **Centralize** across accounts:

  | Need | Use |
  |---|---|
  | see metrics, logs and traces of many accounts in one place | **CloudWatch cross-account observability**: a monitoring account linked to source accounts |
  | ship logs to a central store | **subscription filters** to Firehose (into S3 or OpenSearch), or to a destination in a central account |
  | API activity of every account | the **organization trail** of CloudTrail |
  | keep old logs cheaply | S3 with **lifecycle** rules to colder classes |

## Analyse

- **Metric filters** and **alarms**; **composite alarms**; **anomaly
  detection** alarms, which learn a metric's normal band instead of a fixed
  threshold.
- **Logs Insights** queries; **Contributor Insights** (top-N contributors:
  which IP, which key).
- **X-Ray** traces and **CloudWatch Application Signals** (service-level
  dashboards and SLOs from traces and metrics); **Container Insights** and
  **Lambda Insights** for per-container and per-function detail.
- **Athena** over logs in S3: CloudTrail, ELB access logs, VPC Flow Logs.

## Automate

- **Alarm actions** to SNS, EventBridge and Systems Manager.
- **Dashboards as code** (CloudFormation or CDK), so every environment has
  the same ones.
- **Config rules** and **conformance packs** monitor configuration, and
  **aggregators** collect compliance from all accounts and Regions.
- **Synthetics canaries** test user journeys on a schedule.

| In a question | Answer |
|---|---|
| "one place to see all accounts' metrics and traces" | cross-account observability |
| "the threshold changes with the time of day" | anomaly detection alarm |
| "which client IPs cause the most errors" | Contributor Insights |
| "query a year of CloudTrail logs with SQL" | Athena over the trail's S3 bucket |
| "every instance must run the same agent configuration" | agent config in Parameter Store, applied by State Manager |
| "compliance status of all accounts" | a Config aggregator |

## Traps

- Without the agent there are no memory or disk-space metrics.
- Logs are kept **for ever** by default.
- Metric filters do not process old events.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 4; AWS service documentation.

## Questions from open banks

- 3 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
