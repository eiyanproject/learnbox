#!/usr/bin/env bash
# Publishes learnbox through the Cloudflare tunnel that already runs on the OCI
# host: a Caddy site block, a cloudflared ingress rule, and the DNS route.
#
# RUN ON THE OCI HOST, as root.
#
#   ./setup-oci.sh --learnbox-ip 100.x.y.z                 # plan only
#   ./setup-oci.sh --learnbox-ip 100.x.y.z --yes           # apply
#   ./setup-oci.sh --learnbox-ip 100.x.y.z --host learnbox.example.com --yes
#
# Follows homelab-monitoring/oci/add-dashboard-path.sh: every edit is a marked
# block, the file is backed up first, the result is validated, and a failure
# restores the backup. Re-running replaces the blocks it previously wrote.
#
# It does NOT create the Access application - that is a dashboard step, and it
# is the one that actually keeps strangers out. The script prints it at the end
# along with the update-lxc.sh command that arms learnbox's own token check.
set -euo pipefail

HOST="learnbox.eiyanproject.com"; LEARNBOX_IP=""; CONFIRM="no"
CADDYFILE="/etc/caddy/Caddyfile"; CF_CONFIG="/etc/cloudflared/config.yml"
MARKER="# managed by learnbox setup-oci.sh"

die() { echo "error: $*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)        HOST="$2"; shift 2 ;;
    --learnbox-ip) LEARNBOX_IP="$2"; shift 2 ;;
    --caddyfile)   CADDYFILE="$2"; shift 2 ;;
    --cf-config)   CF_CONFIG="$2"; shift 2 ;;
    --yes)         CONFIRM="yes"; shift ;;
    -h|--help)     sed -n '2,18p' "$0"; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[[ $EUID -eq 0 ]] || die "run as root"
[[ -n "$LEARNBOX_IP" ]] || die "--learnbox-ip is required (the LXC's LAN or Tailscale address)"
[[ "$HOST" =~ ^[a-z0-9.-]+\.[a-z]{2,}$ ]] || die "--host does not look like a hostname: $HOST"
[[ -f "$CADDYFILE" ]] || die "no Caddyfile at $CADDYFILE (pass --caddyfile)"
command -v caddy >/dev/null || die "caddy not on PATH - is this the right host?"

# learnbox must answer before anything is published; a tunnel to a dead origin
# is harder to diagnose from the browser than from here.
echo "==> checking learnbox at ${LEARNBOX_IP}:8080"
health=$(curl -fsS -m 8 "http://${LEARNBOX_IP}:8080/healthz" 2>/dev/null) ||
  die "no answer from ${LEARNBOX_IP}:8080 - is the CT running, and is this host on the same tailnet?"
echo "    $health"

# --------------------------------------------------------------- cloudflared
# Token-managed tunnels keep their ingress in the dashboard; there is no file
# to edit and writing one would be ignored.
CF_MODE="none"
if systemctl cat cloudflared &>/dev/null; then
  if systemctl cat cloudflared | grep -qE -- '--token|TUNNEL_TOKEN'; then
    CF_MODE="token"
  elif [[ -f "$CF_CONFIG" ]]; then
    CF_MODE="file"
  fi
fi

case "$CF_MODE" in
  file)  CF_PLAN="add an ingress rule to $CF_CONFIG, above the catch-all" ;;
  token) CF_PLAN="dashboard-managed (--token): add the Public Hostname by hand, printed below" ;;
  none)  CF_PLAN="cloudflared not found; skipping (install it or pass --cf-config)" ;;
esac

CADDY_BLOCK="${MARKER} - do not edit by hand, re-run the script
http://${HOST} {
	reverse_proxy ${LEARNBOX_IP}:8080
}"

cat <<PLAN

  Plan
  ----
  hostname      ${HOST}
  origin        ${LEARNBOX_IP}:8080   (${health})
  caddyfile     ${CADDYFILE}
  cloudflared   ${CF_PLAN}

  Caddy block to insert (replacing any previous one for this hostname):

$(sed 's/^/    /' <<<"$CADDY_BLOCK")

PLAN

if [[ "$CONFIRM" != "yes" ]]; then
  echo "  Dry run. Nothing was changed. Re-run with --yes to apply."
  exit 0
fi

# --------------------------------------------------------------------- caddy
BACKUP="${CADDYFILE}.bak.$(date +%Y%m%d-%H%M%S)"
cp -a "$CADDYFILE" "$BACKUP"
echo "==> backed up to ${BACKUP}"

TMP=$(mktemp)
# Drop a previous managed block for this host (the marker line plus the site
# block that follows it), then append the new one.
awk -v marker="$MARKER" -v block="$CADDY_BLOCK" '
  skipping {
    depth += gsub(/\{/, "{"); depth -= gsub(/\}/, "}")
    if (depth <= 0) skipping = 0
    next
  }
  index($0, marker) { pending = 1; next }
  pending && /\{[[:space:]]*$/ { pending = 0; depth = 1; skipping = 1; next }
  { pending = 0; print }
  END { print ""; print block }
' "$CADDYFILE" > "$TMP"

grep -q "reverse_proxy ${LEARNBOX_IP}:8080" "$TMP" || { rm -f "$TMP"; die "insertion produced no change - left ${CADDYFILE} alone"; }
cat "$TMP" > "$CADDYFILE"
rm -f "$TMP"

echo "==> validating caddy"
if ! caddy validate --adapter caddyfile --config "$CADDYFILE" >/dev/null 2>&1; then
  cp -a "$BACKUP" "$CADDYFILE"
  die "config did not validate; restored ${BACKUP} and changed nothing"
fi
echo "    ok"

echo "==> reloading caddy"
systemctl reload caddy || { cp -a "$BACKUP" "$CADDYFILE"; systemctl reload caddy || true; die "reload failed; restored ${BACKUP}"; }
echo "    ok"

# --------------------------------------------------------------- ingress rule
if [[ "$CF_MODE" == "file" ]]; then
  CF_BACKUP="${CF_CONFIG}.bak.$(date +%Y%m%d-%H%M%S)"
  cp -a "$CF_CONFIG" "$CF_BACKUP"
  echo "==> backed up to ${CF_BACKUP}"

  TMP=$(mktemp)
  # Rules are matched top to bottom and the last one is a catch-all, so a new
  # hostname has to go above it or it never matches.
  awk -v host="$HOST" -v marker="$MARKER" '
    index($0, marker) { skip = 2; next }       # drop our previous 2-line rule
    skip > 0 { skip--; next }
    !done && /^[[:space:]]*-[[:space:]]*service:/ && !/hostname/ {
      print "  " marker
      print "  - hostname: " host
      print "    service: http://localhost:80"
      done = 1
    }
    { print }
  ' "$CF_CONFIG" > "$TMP"

  grep -q "hostname: ${HOST}" "$TMP" || { rm -f "$TMP"; die "could not find the catch-all rule in ${CF_CONFIG}; add the rule by hand"; }
  cat "$TMP" > "$CF_CONFIG"
  rm -f "$TMP"

  echo "==> validating ingress"
  if ! cloudflared tunnel ingress validate --config "$CF_CONFIG" >/dev/null 2>&1; then
    cp -a "$CF_BACKUP" "$CF_CONFIG"
    die "ingress did not validate; restored ${CF_BACKUP}"
  fi
  echo "    ok"

  echo "==> restarting cloudflared"
  systemctl restart cloudflared || { cp -a "$CF_BACKUP" "$CF_CONFIG"; systemctl restart cloudflared || true; die "restart failed; restored ${CF_BACKUP}"; }
  echo "    ok"
fi

# ------------------------------------------------------------------ what's left
cat <<NEXT

  Done on this host. ${HOST} now reaches learnbox at ${LEARNBOX_IP}:8080.

  --------------------------------------------------------------------------
  1. DNS - point the name at the tunnel (skip if it already resolves)
  --------------------------------------------------------------------------
  cloudflared tunnel route dns <TUNNEL_NAME_OR_ID> ${HOST}
$( [[ "$CF_MODE" == "token" ]] && cat <<TOKENMODE

  --------------------------------------------------------------------------
  1b. This tunnel is dashboard-managed, so add the route there
  --------------------------------------------------------------------------
  Zero Trust > Networks > Tunnels > your tunnel > Public Hostnames > Add:
      subdomain  ${HOST%%.*}
      domain     ${HOST#*.}
      service    HTTP  ->  localhost:80
TOKENMODE
)
  --------------------------------------------------------------------------
  2. ACCESS APPLICATION - this is the gate. Do not skip it.
  --------------------------------------------------------------------------
  Zero Trust > Access > Applications > Add a self-hosted application
      domain   ${HOST}
      policy   Allow, Emails: your address
  Copy the Application Audience (AUD) tag from its Overview.

  --------------------------------------------------------------------------
  3. ARM learnbox's own token check, from the Proxmox host
  --------------------------------------------------------------------------
  bash update-lxc.sh --ctid <CTID> --yes \\
    --access-host ${HOST} \\
    --access-team <yourteam>.cloudflareaccess.com \\
    --access-aud  <the AUD tag from step 2>

  Until step 3, ${HOST} answers 421: learnbox refuses hostnames it was not told
  about, rather than serving a shell to whatever reaches it.

  Verify:  curl -s -o /dev/null -w '%{http_code}\\n' https://${HOST}/
           302 to the Access login page, and 403 from learnbox for a request
           that arrives without a token.

NEXT
