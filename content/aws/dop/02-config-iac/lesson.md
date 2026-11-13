---
title: "Domain 2: Configuration management and IaC"
summary: 17% of the exam. CloudFormation and CDK in depth, deploying to many accounts and Regions, and keeping instances and accounts configured automatically.
order: 2
kind: quiz
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **Parameters**, **Mappings**, **Conditions** | inputs, lookup tables, resources only in some environments |
| **intrinsic functions** | `Ref`, `Fn::GetAtt`, `Fn::Sub`, `Fn::If`: values computed at deploy time |
| **nested stack** | a template used inside another |
| **cross-stack reference** | `Export` / `Fn::ImportValue`; an export cannot change while imported |
| **stack policy** | protects resources from updates |
| **`DeletionPolicy`** / **`UpdateReplacePolicy`** | keep or snapshot a resource on delete / on replacement |
| **`CreationPolicy`** + **`cfn-signal`** | wait for instances to report success |
| **custom resource** | a Lambda function doing what CloudFormation cannot |
| **module**, **macro** | reusable resource groups / template transforms |
| **hook** | a check before resources are created or changed, which can block them |
| **dynamic reference** | `{{resolve:secretsmanager:...}}`: read at deploy time, never stored in the template |
| **StackSets** with **service-managed permissions** | deploy automatically to accounts joining an OU |
| **CDK construct** | a building block, from low-level `Cfn*` to high-level patterns |
| **`cdk synth`**, **`cdk diff`**, **`cdk deploy`** | produce the template / show changes / deploy |
| **CDK bootstrapping** | creates the staging bucket and roles once per account and Region |
| **CDK Pipelines** | self-mutating pipelines that update themselves |
| **Customizations for Control Tower** | apply your baseline to each new account |
| **AWS Service Catalog** | **portfolios** of approved **products** users launch without broad permissions |
| **launch constraint** | the role Service Catalog uses to create the resources |
| **State Manager association** | keeps a configuration applied on a schedule |
| **Distributor** | packages software for installation across fleets |
| **Inventory** | installed software and configuration of instances |
| **AppConfig** | feature flags with **validators** and gradual **deployment strategies** |
| **EC2 Image Builder** | golden AMIs and container images |

---

Everything should be described as code and kept in the state that code
describes: the infrastructure (CloudFormation, CDK), the accounts (Control
Tower, StackSets, Service Catalog) and what runs on the instances (Systems
Manager). This domain goes deeper into CloudFormation than any associate
exam. The method for reading questions is on the Domain 1 page.

**Weight: 17% of the scored questions.**

## CloudFormation in depth

*Practised in Operations lesson 3.*

| Feature | Use |
|---|---|
| **Parameters**, **Mappings**, **Conditions** | inputs, lookup tables (an AMI per Region), resources only in some environments |
| Intrinsic functions (`Ref`, `Fn::GetAtt`, `Fn::Sub`, `Fn::If`...) | values computed at deploy time |
| **Nested stacks** | reuse a template inside another, deployed together |
| **Cross-stack references** (`Export` / `Fn::ImportValue`) | one stack uses another's outputs; an exported value cannot change or be deleted while imported |
| **Change sets** | preview changes, including replacements |
| **Stack policies** | protect resources from updates (for example, no replacement of the database) |
| **`DeletionPolicy`** / **`UpdateReplacePolicy`** | keep or snapshot a resource when it is deleted, or **replaced** by an update |
| **`CreationPolicy`** + `cfn-signal` | wait for instances to report successful bootstrapping |
| **Custom resources** (Lambda-backed) | anything CloudFormation cannot do natively |
| **Modules**, **macros** | reusable resource groups; template transforms |
| **Hooks** | checks that run before resources are created or changed, and can block them |
| **Dynamic references** (`{{resolve:secretsmanager:...}}`, `{{resolve:ssm:...}}`) | secrets and parameters read at deploy time, never stored in the template |

- **StackSets** deploy one template to many accounts and Regions. With
  **service-managed permissions** (through Organizations), they deploy
  **automatically** to accounts that join a target OU, and remove stacks
  from accounts that leave.
- **CDK**: **constructs** (from low-level `Cfn*` to high-level patterns),
  `cdk synth` (produce the template), `cdk diff`, `cdk deploy`;
  **bootstrapping** creates the staging bucket and roles **once per account
  and Region**; **CDK Pipelines** build **self-mutating** pipelines that
  update themselves when their definition changes.

## Multi-account automation

*Practised in Security lesson 3.*

- **Organizations** and **Control Tower**: Account Factory for new
  accounts, and **customizations** (Customizations for Control Tower,
  Account Factory Customization) that apply your baseline to each new
  account.
- **AWS Service Catalog**: **portfolios** of approved **products**
  (CloudFormation templates) that users launch without needing the
  permissions to create the resources themselves; launch constraints supply
  the role.
- **RAM** shares resources (subnets, Transit Gateways, Resolver rules).

## Configuration management

*Practised in Foundations lesson 8, Security lesson 2.*

- **Systems Manager**:
  - **State Manager** associations keep a configuration applied, on a
    schedule;
  - **Run Command** and **Automation** runbooks;
  - **Parameter Store** hierarchies and SecureString;
  - **Distributor** packages software for installation across fleets;
  - **Inventory** of installed software and configuration.
- **AppConfig**: feature flags and dynamic configuration, with
  **validators** (JSON schema or a Lambda function) and **deployment
  strategies** that roll a change out gradually and roll back on an alarm.
- **EC2 Image Builder** for golden AMIs and container images.

| In a question | Answer |
|---|---|
| "keep the old database when an update replaces it" | `UpdateReplacePolicy: Retain` (or `Snapshot`) |
| "prevent updates from replacing the production database" | a stack policy |
| "a resource CloudFormation does not support" | a Lambda-backed custom resource |
| "the template must not contain the password" | a dynamic reference to Secrets Manager |
| "baseline stack in every new account automatically" | StackSets with service-managed permissions and auto deployment |
| "teams launch approved stacks without broad permissions" | Service Catalog |
| "roll out a configuration change gradually, roll back on alarms" | AppConfig |

## Traps

- **`DeletionPolicy`** does not cover **replacement** during updates;
  `UpdateReplacePolicy` does.
- An **exported** output cannot change while another stack imports it.
- The CDK still deploys **through CloudFormation**.

Source: AWS Certified DevOps Engineer - Professional (DOP-C02) exam guide,
Content Domain 2; AWS service documentation.

## Questions from open banks

- 3 questions by **Reneh Majnounian** from github.com/renehmj/aws-trainer (commit 842dc87), MIT licence. Their ids start with `rm-`; each one's reference names the original question.

They are written by their authors as original practice questions, not copied from the exam, and are drawn by the mock exam alongside the questions above. Their wording is unchanged; the answer options are shuffled, and the explanations of the wrong options are joined into one explanation. THIRD-PARTY-NOTICES.md in the repository holds the licences.
