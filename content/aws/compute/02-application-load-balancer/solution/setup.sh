#!/usr/bin/env bash
# Compute 2: an Application Load Balancer.
set -euo pipefail

# The foundations VPC: sets VPC_ID, PUBLIC_A, PUBLIC_B, PRIVATE_A, PRIVATE_B.
eval "$(awslab given vpc)"

# 1. Security groups alb (80 and 443 from anywhere) and web (80 from alb only).
ALB_SG=$(aws ec2 create-security-group --group-name alb --description "load balancer" \
  --vpc-id "$VPC_ID" --query GroupId --output text)
for port in 80 443; do
  aws ec2 authorize-security-group-ingress --group-id "$ALB_SG" \
    --protocol tcp --port "$port" --cidr 0.0.0.0/0 >/dev/null
done
WEB_SG=$(aws ec2 create-security-group --group-name web --description "web tier" \
  --vpc-id "$VPC_ID" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$WEB_SG" \
  --protocol tcp --port 80 --source-group "$ALB_SG" >/dev/null

# 2. Target group web-tg: HTTP:80, instance targets, health check /health -> 200.
TG=$(aws elbv2 create-target-group --name web-tg --protocol HTTP --port 80 \
  --vpc-id "$VPC_ID" --target-type instance \
  --health-check-path /health --matcher HttpCode=200 \
  --query 'TargetGroups[0].TargetGroupArn' --output text)

# 3. The internet-facing ALB web-alb in public-a and public-b, group alb.
ALB=$(aws elbv2 create-load-balancer --name web-alb --type application \
  --scheme internet-facing --subnets "$PUBLIC_A" "$PUBLIC_B" \
  --security-groups "$ALB_SG" \
  --query 'LoadBalancers[0].LoadBalancerArn' --output text)

# 4. An ACM certificate for www.example.com; HTTPS:443 forwarding to web-tg;
#    HTTP:80 redirecting to HTTPS with a 301.
CERT=$(aws acm request-certificate --domain-name www.example.com \
  --validation-method DNS --query CertificateArn --output text)
aws elbv2 create-listener --load-balancer-arn "$ALB" --protocol HTTPS --port 443 \
  --certificates CertificateArn="$CERT" \
  --default-actions Type=forward,TargetGroupArn="$TG" >/dev/null
aws elbv2 create-listener --load-balancer-arn "$ALB" --protocol HTTP --port 80 \
  --default-actions 'Type=redirect,RedirectConfig={Protocol=HTTPS,Port=443,StatusCode=HTTP_301}' >/dev/null
