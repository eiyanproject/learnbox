#!/usr/bin/env bash
# Creates the learnbox LXC on a Proxmox node, clones this repo into it and
# runs the install.
#
# RUN THIS ON THE PROXMOX HOST (not inside a container). Standalone - it does
# not need the rest of the repo next to it:
#
#   curl -fsSLO https://raw.githubusercontent.com/eiyanproject/learnbox/main/scripts/create-lxc.sh
#   bash create-lxc.sh --ctid 116 --ip 192.168.0.116/24          # plan only
#   bash create-lxc.sh --ctid 116 --ip 192.168.0.116/24 --yes    # apply
#
# Nothing is created until you pass --yes. Without it you get the plan only.
set -euo pipefail

CTID=""; HOSTNAME_="learnbox"; IP=""; GW="192.168.0.1"
STORAGE="local-lvm"; DISK="15"; MEMORY="2048"; SWAP="1024"; CORES="2"; BRIDGE="vmbr0"
REPO="https://github.com/eiyanproject/learnbox.git"; BRANCH="main"; DIR="/opt/learnbox"
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
    --repo)     REPO="$2"; shift 2 ;;
    --branch)   BRANCH="$2"; shift 2 ;;
    --yes)      CONFIRM="yes"; shift ;;
    -h|--help)  sed -n '2,13p' "$0"; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

command -v pct >/dev/null || die "pct not found - run this on the Proxmox host"
[[ -n "$CTID" ]] || die "--ctid is required (pvesh get /cluster/nextid suggests one)"
[[ -n "$IP"   ]] || die "--ip is required (CIDR, e.g. 192.168.0.116/24)"

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
  repo          ${REPO} (${BRANCH}) -> ${DIR}

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
  pct exec "$CTID" -- getent hosts github.com &>/dev/null && break
  sleep 2
done

echo "==> cloning repo"
pct exec "$CTID" -- bash -lc "
  set -e
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq ca-certificates git >/dev/null
  rm -rf '${DIR}'
  git clone --branch '${BRANCH}' '${REPO}' '${DIR}'
"

echo "==> installing"
pct exec "$CTID" -- bash "${DIR}/scripts/install.sh"

cat <<DONE

  Done. learnbox is at http://${IP%%/*}:8080

  To open it by name as well as by IP, add the name to LEARNBOX_ALLOWED_HOSTS
  in /etc/learnbox.env inside the CT, then: systemctl restart learnbox

  Update later, from this host:
    bash update-lxc.sh --ctid ${CTID} --snapshot --yes
  or inside the container:
    ${DIR}/scripts/update.sh

  To join monitoring, from homelab-monitoring/scripts on this host:
    ./setup-guest-logging.sh --collector <this node's mon IP> --yes --only ${CTID}
  and add ${IP%%/*}:8080 to targets/services.json in the mon LXC.

DONE
