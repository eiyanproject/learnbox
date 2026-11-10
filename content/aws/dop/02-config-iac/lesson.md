---
title: "Domain 2: Configuration management and IaC"
summary: 17% of the exam. CloudFormation and CDK in depth, deploying to many accounts and Regions, and keeping instances and accounts configured automatically.
order: 2
kind: quiz
---

**Weight: 17% of the scored questions.**

## Infrastructure as code

- **CloudFormation**: parameters, mappings, conditions, intrinsic
  functions, nested stacks and cross-stack references (Export /
  Fn::ImportValue), change sets, stack policies, DeletionPolicy and
  UpdateReplacePolicy, CreationPolicy with cfn-signal, custom resources
  (Lambda-backed), modules, macros, **Hooks** for proactive checks,
  dynamic references to Secrets Manager and Parameter Store.
- **StackSets** across accounts and Regions with service-managed
  permissions and automatic deployment to OUs.
- **CDK**: constructs, `cdk synth`/`diff`/`deploy`, bootstrapping per
  account/Region, CDK Pipelines for self-mutating pipelines.

## Multi-account automation

- Organizations, Control Tower (Account Factory, customizations),
  **AWS Service Catalog** portfolios for approved products,
  RAM for sharing.

## Configuration management

- **Systems Manager**: State Manager associations, Run Command,
  Automation runbooks, Parameter Store (hierarchies, SecureString),
  Distributor, inventory, AppConfig for feature flags and dynamic
  configuration with validators and deployment strategies.
- **EC2 Image Builder** for golden AMIs and container images.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 2; AWS service documentation.

## Questions from open banks

- 3 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
