#!/usr/bin/env bash
# Creates the learnbox LXC on a Proxmox node and provisions it.
#
# RUN THIS ON THE PROXMOX HOST. provision.sh must sit next to this script.
#
#   ./create-ct.sh --ctid 116 --ip 192.168.0.116/24          # plan only
#   ./create-ct.sh --ctid 116 --ip 192.168.0.116/24 --yes    # apply
#
# Nothing is created until you pass --yes. Without it you get the plan only.
set -euo pipefail

CTID=""; HOSTNAME_="learnbox"; IP=""; GW="192.168.0.1"
STORAGE="local-lvm"; DISK="15"; MEMORY="2048"; SWAP="1024"; CORES="2"; BRIDGE="vmbr0"
CONFIRM="no"

die() { echo "error: $*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ctid)     CTID="$2"; shift 2 ;;
    --hostname) HOSTNAME_="$2"; shift 2 ;;
    --ip)       IP="$2"; shift 2 ;;
    --gw)       GW="$2"; shift 2 ;;
    --storage)  STORAGE="$2"; shift 2 ;;
    --disk)     DISK="$2"; shift 2 ;;
    --memory)   MEMORY="$2"; shift 2 ;;
    --swap)     SWAP="$2"; shift 2 ;;
    --cores)    CORES="$2"; shift 2 ;;
    --bridge)   BRIDGE="$2"; shift 2 ;;
    --yes)      CONFIRM="yes"; shift ;;
    -h|--help)  sed -n '2,9p' "$0"; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

command -v pct >/dev/null || die "pct not found - run this on the Proxmox host"
[[ -n "$CTID" ]] || die "--ctid is required"
[[ -n "$IP"   ]] || die "--ip is required (CIDR, e.g. 192.168.0.116/24)"

here="$(cd "$(dirname "$0")" && pwd)"
[[ -f "$here/provision.sh" ]] || die "provision.sh not found next to $0"

# VMIDs are unique across the whole CLUSTER. `pct status` only knows this
# node's guests, so check the cluster first.
if pvesh get /cluster/resources --type vm --output-format json 2>/dev/null \
     | grep -qE "\"vmid\":\s*${CTID}[,}]"; then
  suggested=$(pvesh get /cluster/nextid 2>/dev/null || true)
  die "CTID $CTID is already in use somewhere in this cluster${suggested:+ - next free id is $suggested}"
fi
pct status "$CTID" &>/dev/null && die "CTID $CTID already exists on this node - pick another"

# Use a Debian 13 template that is already downloaded, newest first.
TEMPLATE=$(pveam list local 2>/dev/null | awk '/debian-13-standard/ {print $1}' | sort -V | tail -1 || true)
[[ -n "$TEMPLATE" ]] || die "no debian-13-standard template in 'local' - pveam download local <name>"

cat <<PLAN

  Plan
  ----
  node          $(hostname)
  container     $CTID  ($HOSTNAME_)
  resources     ${CORES} cores, ${MEMORY} MB RAM + ${SWAP} MB swap, ${DISK} GB on ${STORAGE}
  network       ${IP} via ${GW} on ${BRIDGE}
  features      nesting=1  (systemd in unprivileged Debian 13; cgroup delegation for the shell)
  template      ${TEMPLATE}

PLAN

if [[ "$CONFIRM" != "yes" ]]; then
  echo "  Dry run. Nothing was created. Re-run with --yes to apply."
  exit 0
fi

echo "==> creating container $CTID"
pct create "$CTID" "$TEMPLATE" \
  --hostname "$HOSTNAME_" --ostype debian \
  --cores "$CORES" --memory "$MEMORY" --swap "$SWAP" \
  --rootfs "${STORAGE}:${DISK}" \
  --net0 "name=eth0,bridge=${BRIDGE},ip=${IP},gw=${GW}" \
  --features nesting=1 \
  --unprivileged 1 --onboot 1

echo "==> starting"
pct start "$CTID"

echo "==> waiting for network"
for _ in $(seq 1 30); do
  pct exec "$CTID" -- getent hosts deb.debian.org &>/dev/null && break
  sleep 2
done

echo "==> provisioning"
pct push "$CTID" "$here/provision.sh" /root/provision.sh --perms 0755
pct exec "$CTID" -- /root/provision.sh

cat <<DONE

  Done. learnbox is at ${IP%%/*}

  To join monitoring, from homelab-monitoring/scripts on this host:
    ./setup-guest-logging.sh --collector <this node's mon IP> --yes --only ${CTID}

DONE
