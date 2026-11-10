---
title: "Domain 3: Deployment, provisioning and automation"
summary: 22% of the exam. Golden images, CloudFormation and the CDK, deploying across accounts and Regions, fixing stacks that fail, and Systems Manager doing the routine work.
order: 3
kind: quiz
---

**Weight: 22% of the scored questions.**

- **Images**: **EC2 Image Builder** pipelines build, test and distribute
  patched AMIs and container images on a schedule.
- **CloudFormation**: change sets, drift detection, `DeletionPolicy`
  (Retain, Snapshot), **CreationPolicy** with `cfn-signal` so a stack waits
  for instances to finish bootstrapping, `UPDATE_ROLLBACK_FAILED` and
  *continue update rollback*. The **CDK** synthesizes CloudFormation.
- **Many accounts and Regions**: **StackSets** deploy one template to many
  accounts and Regions (with Organizations, automatically to new accounts);
  **AWS RAM** shares resources such as subnets, Transit Gateways and
  license configurations.
- **Deployment problems**: subnets too small for the IP addresses a service
  needs, missing IAM permissions (and `iam:PassRole`), quotas.
- **Systems Manager**: **Run Command** (scripts across a fleet, no SSH),
  **State Manager** (keep configuration applied), **Session Manager** (shell
  access with IAM and logging, no bastions or open ports), **Parameter
  Store**, **Automation**. Instances need the SSM Agent, a role with
  `AmazonSSMManagedInstanceCore`, and a path to the SSM endpoints.
- **Event-driven automation**: EventBridge rules and schedules, S3 event
  notifications, Lambda.

Source: AWS Certified CloudOps Engineer - Associate (SOA-C03) exam guide,
Content Domain 3; AWS service documentation.

## Questions from open banks

- 65 questions by **zghanw** from github.com/zghanw/aws-cloudops-engineer-associate (commit c2e7acc), MIT licence. Their ids start with `zg-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
