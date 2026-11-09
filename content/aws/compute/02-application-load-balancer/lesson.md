---
title: An Application Load Balancer
summary: One HTTPS front door across two AZs - security groups that only let the load balancer reach the servers, a target group with health checks, an ACM certificate, and HTTP redirected to HTTPS.
order: 2
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "`aws elbv2 create-load-balancer --name web-alb --type application --scheme internet-facing --subnets \"$PUBLIC_A\" \"$PUBLIC_B\" --security-groups \"$ALB_SG\" --query 'LoadBalancers[0].LoadBalancerArn' --output text`."
  - "`aws elbv2 create-target-group --name web-tg --protocol HTTP --port 80 --vpc-id \"$VPC_ID\" --target-type instance --health-check-path /health --matcher HttpCode=200 --query 'TargetGroups[0].TargetGroupArn' --output text`."
  - "The certificate: `CERT=$(aws acm request-certificate --domain-name www.example.com --validation-method DNS --query CertificateArn --output text)`. The HTTPS listener: `aws elbv2 create-listener --load-balancer-arn \"$ALB\" --protocol HTTPS --port 443 --certificates CertificateArn=\"$CERT\" --default-actions Type=forward,TargetGroupArn=\"$TG\"`."
  - "The redirect: `--protocol HTTP --port 80 --default-actions 'Type=redirect,RedirectConfig={Protocol=HTTPS,Port=443,StatusCode=HTTP_301}'`."
---

An **Application Load Balancer** (ALB) takes HTTP and HTTPS requests and
spreads them over healthy **targets** - instances, IP addresses, Lambda
functions - across Availability Zones. It works at layer 7: it can route by
host name or path, terminate TLS, redirect, and return fixed responses.

## The pieces

- **Load balancer**: in at least two public subnets in different AZs, with
  a security group. `internet-facing` gets public DNS; `internal` serves
  only the VPC.
- **Target group**: the set of targets and how to check them. The **health
  check** (path, interval, thresholds) decides which targets get traffic.
- **Listener**: a port and protocol on the load balancer, with rules that
  forward, redirect or respond.

## Security groups that chain

The load balancer's group allows 80 and 443 from the internet. The web
servers' group allows 80 **only from the load balancer's group** - so the
servers cannot be reached around it, whatever their addresses.

## TLS at the load balancer

The HTTPS listener holds a certificate from **ACM**: free for public
certificates, renewed automatically once validated (by a DNS record you add,
or by email). The ALB decrypts and forwards to the targets - over plain HTTP
inside the VPC here, or re-encrypted if required. A second listener on port
80 does nothing but redirect to HTTPS.

(In this sandbox the certificate stays `PENDING_VALIDATION` - there is no DNS
to validate it against - which the emulator accepts.)

## ALB, NLB or GWLB?

| | Works at | For |
|---|---|---|
| **Application** | layer 7 (HTTP/HTTPS, gRPC) | web apps, path/host routing, WAF, OIDC auth |
| **Network** | layer 4 (TCP/UDP/TLS) | extreme performance, static IPs, non-HTTP |
| **Gateway** | layer 3 | inline firewalls and appliances |

## Your task

On top of the foundations VPC:

1. security group **`alb`**: TCP 80 and 443 from anywhere; security group
   **`web`**: TCP 80 **only from `alb`**;
2. target group **`web-tg`**: HTTP on port 80, instance targets, health
   check on **`/health`** expecting **200**;
3. an **internet-facing** ALB **`web-alb`** in **public-a and public-b** with
   the `alb` group;
4. an **ACM certificate** for `www.example.com`, an **HTTPS:443** listener
   with it forwarding to `web-tg`, and an **HTTP:80** listener that
   **redirects to HTTPS with a 301**.
