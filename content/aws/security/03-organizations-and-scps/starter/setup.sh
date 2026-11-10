#!/usr/bin/env bash
# Security 3: Organizations and service control policies.
set -euo pipefail

# 1. The organization (all features), with SCPs and tag policies enabled.


# 2. OUs Security and Workloads under the root; Prod and Dev under Workloads.


# 3. Accounts log-archive (Security), app-prod (Prod), app-dev (Dev).


# 4. SCP baseline-guardrails on the root: no leaving the organization, no
#    stopping or changing CloudTrail, no deleting GuardDuty detectors.


# 5. SCP region-guard on Workloads: only us-east-1 and eu-west-1, except
#    global services.


# 6. SCP dev-instance-types on Dev: only t3.* and t4g.* instances.


# 7. Tag policy cost-center on the root, key CostCenter.

