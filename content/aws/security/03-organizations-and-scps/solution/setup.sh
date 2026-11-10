#!/usr/bin/env bash
# Security 3: Organizations and service control policies.
set -euo pipefail

# 1. The organization (all features), with SCPs and tag policies enabled.
aws organizations create-organization --feature-set ALL >/dev/null
ROOT=$(aws organizations list-roots --query 'Roots[0].Id' --output text)
aws organizations enable-policy-type --root-id "$ROOT" --policy-type SERVICE_CONTROL_POLICY >/dev/null
aws organizations enable-policy-type --root-id "$ROOT" --policy-type TAG_POLICY >/dev/null

# 2. OUs Security and Workloads under the root; Prod and Dev under Workloads.
ou() {
  aws organizations create-organizational-unit --parent-id "$1" --name "$2" \
    --query OrganizationalUnit.Id --output text
}
SECURITY=$(ou "$ROOT" Security)
WORKLOADS=$(ou "$ROOT" Workloads)
PROD=$(ou "$WORKLOADS" Prod)
DEV=$(ou "$WORKLOADS" Dev)

# 3. Accounts log-archive (Security), app-prod (Prod), app-dev (Dev).
account() {  # name, OU: create, wait, move
  local req id state
  req=$(aws organizations create-account --email "$1@example.com" --account-name "$1" \
    --query CreateAccountStatus.Id --output text)
  for _ in $(seq 30); do
    state=$(aws organizations describe-create-account-status --create-account-request-id "$req" \
      --query CreateAccountStatus.State --output text)
    [ "$state" = SUCCEEDED ] && break
    [ "$state" = FAILED ] && { echo "creating $1 failed" >&2; return 1; }
    sleep 2
  done
  id=$(aws organizations describe-create-account-status --create-account-request-id "$req" \
    --query CreateAccountStatus.AccountId --output text)
  aws organizations move-account --account-id "$id" --source-parent-id "$ROOT" \
    --destination-parent-id "$2"
}
account log-archive "$SECURITY"
account app-prod "$PROD"
account app-dev "$DEV"

scp() {  # name, target, JSON
  local id
  id=$(aws organizations create-policy --name "$1" --type SERVICE_CONTROL_POLICY \
    --description "$1" --content "$3" --query Policy.PolicySummary.Id --output text)
  aws organizations attach-policy --policy-id "$id" --target-id "$2"
}

# 4. SCP baseline-guardrails on the root.
scp baseline-guardrails "$ROOT" '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ProtectOrgAndAudit",
    "Effect": "Deny",
    "Action": ["organizations:LeaveOrganization", "cloudtrail:StopLogging",
               "cloudtrail:DeleteTrail", "cloudtrail:UpdateTrail",
               "guardduty:DeleteDetector"],
    "Resource": "*"
  }]
}'

# 5. SCP region-guard on Workloads.
scp region-guard "$WORKLOADS" '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyOutsideApprovedRegions",
    "Effect": "Deny",
    "NotAction": ["iam:*", "organizations:*", "sts:*", "route53:*",
                  "cloudfront:*", "support:*"],
    "Resource": "*",
    "Condition": {"StringNotEquals": {"aws:RequestedRegion": ["us-east-1", "eu-west-1"]}}
  }]
}'

# 6. SCP dev-instance-types on Dev.
scp dev-instance-types "$DEV" '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "OnlyBurstableInstances",
    "Effect": "Deny",
    "Action": "ec2:RunInstances",
    "Resource": "arn:aws:ec2:*:*:instance/*",
    "Condition": {"StringNotLike": {"ec2:InstanceType": ["t3.*", "t4g.*"]}}
  }]
}'

# 7. Tag policy cost-center on the root, key CostCenter.
TAG_ID=$(aws organizations create-policy --name cost-center --type TAG_POLICY \
  --description "standard CostCenter tag" \
  --content '{"tags": {"CostCenter": {"tag_key": {"@@assign": "CostCenter"}}}}' \
  --query Policy.PolicySummary.Id --output text)
aws organizations attach-policy --policy-id "$TAG_ID" --target-id "$ROOT"
