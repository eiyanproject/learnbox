# Reaching learnbox from outside the house

Target: `https://learnbox.eiyanproject.com`, reachable only by you.

learnbox hands out a **root-capable workspace and a real shell**. It has no
login of its own, so every layer here matters. Do not shorten this setup, and
never open a port on the router.

The path is the same one `l18.` and `cms.` already use:

```
you ─https─▶ Cloudflare edge ─Access check─▶ Tunnel ─▶ OCI box
                                                      cloudflared ─▶ Caddy
                                                                      │ Tailscale
                                                                      ▼
                                                        learnbox LXC :8080
```

Three protections, each independent:

1. **Cloudflare Access** in front: one-time PIN to your email address; nobody
   else ever reaches the origin.
2. **learnbox verifies the Access token itself.** Requests arriving with the
   hostname `learnbox.eiyanproject.com` must carry a valid, unexpired
   Cloudflare Access JWT signed by your team, with the right audience tag. If
   Access is removed, misconfigured, or bypassed, learnbox answers 403.
3. **No open ports.** The tunnel dials out; the LXC is only reachable on the LAN
   and over Tailscale.

LAN and Tailscale access by IP keep working unchanged, without a token.

---

## 1. Cloudflare: application and DNS

In the Cloudflare dashboard (Zero Trust → Access → Applications):

1. **Add an application** → Self-hosted.
   - Application domain: `learnbox.eiyanproject.com`
   - Session duration: whatever you like (24 h is comfortable).
2. **Policy**: Action *Allow*, Include → *Emails* → your address. That is the
   only rule; leave no bypass rule.
3. After saving, open the application's **Overview** and copy the
   **Application Audience (AUD) tag** (a long hex string).
4. Note your **team domain**: Zero Trust → Settings → Custom Pages shows
   `https://<team>.cloudflareaccess.com`. You need `<team>.cloudflareaccess.com`.
5. **DNS** (the `eiyanproject.com` zone): add a CNAME
   `learnbox` → `<tunnel-id>.cfargotunnel.com`, **proxied** (orange cloud).
   The tunnel id is the same one the other hostnames use.

## 2. OCI box: tunnel ingress and Caddy

Two files, exactly as when `l18.` was added.

`/etc/cloudflared/config.yml` — add **above** the `http_status:404` catch-all:

```yaml
  - hostname: learnbox.eiyanproject.com
    service: http://localhost:80
```

Then check that the rule really matches and restart:

```bash
sudo cloudflared tunnel --config /etc/cloudflared/config.yml ingress rule https://learnbox.eiyanproject.com
sudo systemctl restart cloudflared
```

Caddy — add a site block (replace `<learnbox-ip>` with the LXC's LAN address):

```caddyfile
http://learnbox.eiyanproject.com {
    reverse_proxy <learnbox-ip>:8080
}
```

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Caddy passes the original `Host` header and the `Cf-Access-Jwt-Assertion`
header through, and proxies WebSockets (the terminal) without extra
configuration.

The OCI box reaches the LXC over the Tailscale subnet route that already serves
`192.168.0.0/24`. Check it first: `curl -s -o /dev/null -w '%{http_code}\n' http://<learnbox-ip>:8080/healthz` should print `200`.

## 3. learnbox LXC: accept the hostname and enforce the token

Edit `/etc/learnbox.env`:

```bash
LEARNBOX_ACCESS_HOSTS=learnbox.eiyanproject.com
LEARNBOX_ACCESS_TEAM_DOMAIN=<team>.cloudflareaccess.com
LEARNBOX_ACCESS_AUD=<the AUD tag from step 1.3>
```

```bash
systemctl restart learnbox
journalctl -u learnbox -n 20
```

The log should show `cloudflare access enforced`. If it shows the warning about
`LEARNBOX_ACCESS_HOSTS` being set without a team domain and audience, the
hostname is refused with 503 until you fill both in: that is deliberate, so a
half-finished setup cannot expose a shell.

Hostnames in `LEARNBOX_ACCESS_HOSTS` do not need to be repeated in
`LEARNBOX_ALLOWED_HOSTS`.

## 4. Check it

- `https://learnbox.eiyanproject.com` in a browser: Cloudflare asks for your
  email, sends a PIN, and then learnbox loads. Open a lesson terminal and type a
  command: WebSockets work through the tunnel.
- Without a token, from anywhere:

  ```bash
  curl -sS -o /dev/null -w '%{http_code}\n' https://learnbox.eiyanproject.com/healthz
  ```

  Cloudflare answers with a redirect to the login page (302); it never reaches
  learnbox. If you ever see `200` here, stop and re-check the Access policy.

- Spoofing the hostname from inside the LAN is also refused:

  ```bash
  curl -sS -H 'Host: learnbox.eiyanproject.com' http://<learnbox-ip>:8080/healthz
  # {"error":"access denied"}
  ```

- LAN access still works: `http://<learnbox-ip>:8080`.

## Troubleshooting

- **`unknown host "learnbox.eiyanproject.com"` (421) on the public URL**:
  `/etc/learnbox.env` does not list the hostname in `LEARNBOX_ACCESS_HOSTS`.
  Do **not** put it in `LEARNBOX_ALLOWED_HOSTS` instead: that accepts the name
  without checking the Access token and would expose the shell to anyone who can
  reach the tunnel. Finish step 3 (all three `LEARNBOX_ACCESS_*` values), then
  `systemctl restart learnbox`.
- **`Cloudflare` answers 200/421 instead of a 302 to the login page** in step 4:
  the Access application does not cover the hostname yet (step 1). Fix that
  before anything else; learnbox's own token check is the second layer, not the
  first.
- **503 "requires Cloudflare Access verification"**: the hostname is set but the
  team domain or audience tag is missing.
- **403 "access denied"**: the token is missing, expired, or for a different
  audience; `journalctl -u learnbox` logs the reason.

## Notes

- **Session expiry**: the browser keeps a `CF_Authorization` cookie for the
  session duration you set. An open terminal WebSocket is not interrupted when
  it expires, but the next page load asks for a PIN again.
- **Rotation**: Cloudflare rotates signing keys; learnbox re-fetches them
  automatically (hourly, or immediately when it sees an unknown key id).
- **If you stop using the hostname**, remove it from `LEARNBOX_ACCESS_HOSTS`,
  delete the Access application, the DNS record, the ingress rule and the Caddy
  block. Leaving a DNS record pointing at a tunnel with no Access policy is the
  one dangerous combination.
- Do not put learnbox behind a plain Cloudflare proxy without Access, a
  "hidden" URL, or basic auth in Caddy alone. It is a shell.
