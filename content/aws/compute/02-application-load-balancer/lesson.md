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

One web server is a single point of failure: when it crashes, or its AZ
fails, the site is down, and it can only take so much traffic. The fix is
several servers, in more than one AZ, with something in front that spreads
requests over them and stops sending traffic to any that break. That is a
**load balancer**, and visitors only ever see its one address.

An **Application Load Balancer** (ALB) takes HTTP and HTTPS requests and
spreads them over healthy **targets** (instances, IP addresses, Lambda
functions) across Availability Zones. It understands HTTP, so it can also
route by host name or URL path, handle the TLS encryption itself, redirect,
and answer with fixed responses.

```text
 browser ──HTTPS 443──> ALB web-alb (public-a + public-b, security group alb)
                          │  listener 443: decrypt, forward to target group web-tg
                          │  listener 80:  answer "301, go to https://"
                          v
                 target group web-tg: health check GET /health -> expect 200
                    ├── instance in private-a  (security group web: port 80 from alb only)
                    └── instance in private-b
```

## The pieces

An ALB is three resources, created separately and linked by their ARNs:

- **Load balancer**: placed in at least two subnets in different AZs (AWS
  runs a copy of it in each, so it survives an AZ failure; real AWS refuses
  one subnet), with a security group. An **internet-facing** one gets a
  public DNS name, such as `web-alb-1.us-east-1.elb.amazonaws.com`; an
  **internal** one is only reachable inside the VPC.
- **Target group**: a set of targets, the protocol and port to send them
  traffic on, and how to check them. The **health check** requests a path
  (here `/health`) on each target every few seconds; a target that answers
  with the expected status code (`200`, "OK") a few times in a row is
  **healthy** and gets traffic, one that fails is taken out of rotation
  until it recovers.
- **Listener**: a port and protocol the load balancer accepts connections
  on, with a **default action** (forward to a target group, redirect, or
  return a fixed response) and optional rules (for example "path `/api/*`
  goes to another target group").

The load balancer and the target group can be created in either order; the
listener needs both ARNs, so it comes last. The ARNs are long, so capture
them, for example with `--query 'LoadBalancers[0].LoadBalancerArn' --output
text` (the create calls return a list, hence the `[0]`).

## Security groups that chain

Two security groups, one referring to the other (Foundations lesson 8):

- the load balancer's group, **`alb`**, allows 80 and 443 from anywhere:
  it is the public front door;
- the web servers' group, **`web`**, allows 80 **only from the `alb`
  group**.

So the servers cannot be reached **around** the load balancer, whatever
their addresses, and every request goes through the ALB's health checks
and TLS handling.

## TLS at the load balancer

HTTPS needs a **certificate**: a file that proves to browsers that this
server really is `www.example.com`, signed by an authority browsers trust.
**ACM** (AWS Certificate Manager) issues certificates for free for use on
AWS load balancers and CloudFront, and renews them automatically. ACM must
first check that you control the domain, by **DNS validation** (you add a
DNS record it gives you) or by email; until then the certificate's status
is `PENDING_VALIDATION`.

A certificate covers the names written in it, exactly. A **wildcard**
certificate for `*.example.com` covers `www.example.com` and
`shop.example.com`, but **not** `example.com` itself, and not
`a.b.example.com`: the `*` stands for exactly one label. Browsers reject a
name the certificate does not cover.

The HTTPS listener holds the certificate and **terminates** TLS: it
decrypts each request and forwards it to the targets, over plain HTTP
inside the VPC here, or re-encrypted if a compliance rule requires
encryption all the way. The servers then need no certificates of their own.

A second listener, on port 80, does nothing but **redirect** visitors who
typed `http://` to `https://`, with status **301** ("moved permanently";
browsers remember it). The redirect's settings use the CLI's shorthand
syntax, in single quotes so the shell leaves the braces alone:

```
--default-actions 'Type=redirect,RedirectConfig={Protocol=HTTPS,Port=443,StatusCode=HTTP_301}'
```

## ALB, NLB or GWLB?

Elastic Load Balancing has three kinds of load balancer. The exam expects
you to pick:

| | Works at | Understands | Use it for |
|---|---|---|---|
| **Application** (ALB) | layer 7 | HTTP, HTTPS, gRPC: paths, hosts, headers | web apps and APIs, path or host routing, AWS WAF, user sign-in (OIDC) at the load balancer |
| **Network** (NLB) | layer 4 | TCP, UDP, TLS connections only | very high throughput and low latency, **static IP addresses**, non-HTTP protocols |
| **Gateway** (GWLB) | layer 3 | IP packets | sending traffic through third-party firewalls and inspection appliances |

("Layer" refers to the network model: layer 7 is the application's own
protocol, layer 4 connections and ports, layer 3 IP addresses.)

## More load balancer features

- **Targets** of an ALB can be instances, IP addresses (including servers in
  your data centre) or Lambda functions. Health checks are set per target
  group.
- The servers see the **load balancer's** address as the source of every
  request; the client's real address arrives in the `X-Forwarded-For`
  header.
- **Sticky sessions** send each client to the same target, using a cookie,
  at the cost of uneven load.
- **Cross-zone load balancing** spreads requests over targets in all AZs;
  it is on by default for ALBs (free), off for NLBs.
- **Deregistration delay** gives requests in progress time to finish when a
  target is removed: 300 seconds by default.
- With **SNI** (Server Name Indication), one HTTPS listener can hold several
  certificates, one per domain, and picks the one the browser asks for.
- Exam triggers for an **NLB**: UDP, millions of requests per second, or a
  **static IP** (one per AZ) that partners can allow-list. The **Classic
  Load Balancer** is legacy.

## Your task

On top of the Foundations VPC:

1. a security group **`alb`** whose inbound rules are exactly TCP 80 and
   TCP 443 from anywhere, and a security group **`web`** whose only inbound
   rule is TCP 80 **from the `alb` group**;
2. a target group **`web-tg`**: protocol HTTP, port 80, in the VPC,
   **instance** targets, health check on the path **`/health`** expecting
   the code **200** (`--matcher HttpCode=200`);
3. an **internet-facing** Application Load Balancer **`web-alb`** in
   **public-a and public-b**, with the `alb` group and no other;
4. an **ACM certificate** for `www.example.com` (DNS validation), an
   **HTTPS** listener on **443** using it and forwarding to `web-tg`, and an
   **HTTP** listener on **80** that **redirects to HTTPS on 443 with a
   301**.

No instances yet: lesson 3's Auto Scaling group registers them in the target
group. Users reach the ALB by its **DNS name**, never by an IP address: its
addresses change as AWS scales it, so DNS records for your own domain point
at it with a Route 53 **alias** record (section 8), not an A record holding
an IP. After **Run**:

```
$ aws elbv2 describe-load-balancers --names web-alb --query 'LoadBalancers[0].[DNSName,Scheme,State.Code]'
[
    "web-alb-1.us-east-1.elb.amazonaws.com",
    "internet-facing",
    "active"
]
```

and `aws elbv2 describe-listeners --load-balancer-arn "<the ARN>" --query
'Listeners[].[Port,Protocol,DefaultActions[0].Type]' --output table` lists
443 `forward` and 80 `redirect`. The certificate stays
`PENDING_VALIDATION` here, since there is no DNS to validate it against,
which the emulator accepts; a real HTTPS listener needs an issued one.

💸 In a real account an ALB is billed for every hour it exists, plus a
charge for the traffic it handles, whether or not anything is behind it.

## Check yourself

1. Why does the `web` group allow port 80 only from the `alb` group?
   *So the servers cannot be reached around the load balancer.*
2. A target fails `/health`. What happens?
   *It gets no traffic until it passes again.*
3. Which load balancer gives a static IP address?
   *A Network Load Balancer.*
4. How does a server behind an ALB learn the client's IP?
   *From the `X-Forwarded-For` header.*
5. Does `*.example.com` cover `example.com`?
   *No: the wildcard is exactly one label.*
