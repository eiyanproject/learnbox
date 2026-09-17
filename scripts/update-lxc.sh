#!/usr/bin/env bash
# Updates the learnbox LXC from the Proxmox host: optional snapshot, then
# runs the in-container update (pull, re-install).
#
# RUN THIS ON THE PROXMOX HOST. Standalone, like create-lxc.sh:
#
#   curl -fsSLO https://raw.githubusercontent.com/eiyanproject/learnbox/main/scripts/update-lxc.sh
#   bash update-lxc.sh --ctid 116                     # plan only
#   bash update-lxc.sh --ctid 116 --snapshot --yes    # rollback point, then update
#
# Nothing is changed until you pass --yes. Without it you get the plan only.
set -euo pipefail

CTID=""; DIR="/opt/learnbox"; SNAPSHOT="no"; CONFIRM="no"

die() { echo "error: $*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ctid)     CTID="$2"; shift 2 ;;
    --dir)      DIR="$2"; shift 2 ;;
    --snapshot) SNAPSHOT="yes"; shift ;;
    --yes)      CONFIRM="yes"; shift ;;
    -h|--help)  sed -n '2,11p' "$0"; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

command -v pct >/dev/null || die "pct not found - run this on the Proxmox host"
[[ -n "$CTID" ]] || die "--ctid is required"
pct status "$CTID" &>/dev/null || die "CTID $CTID does not exist on this node"
[[ "$(pct status "$CTID")" == "status: running" ]] || die "CTID $CTID is not running"
pct exec "$CTID" -- test -d "$DIR/.git" \
  || die "$DIR is not a git checkout inside CT $CTID (use --dir)"

CURRENT=$(pct exec "$CTID" -- git -C "$DIR" rev-parse --short HEAD 2>/dev/null || echo "?")
pct exec "$CTID" -- git -C "$DIR" fetch -q 2>/dev/null || true
LATEST=$(pct exec "$CTID" -- git -C "$DIR" rev-parse --short '@{u}' 2>/dev/null || echo "?")
SNAPNAME="pre_update_$(date +%Y%m%d_%H%M)"

cat <<PLAN

  Plan
  ----
  container     $CTID  ($(pct config "$CTID" | awk '/^hostname:/ {print $2}'))
  checkout      $DIR
  version       $CURRENT -> $LATEST
  snapshot      $( [[ "$SNAPSHOT" == "yes" ]] && echo "$SNAPNAME" || echo "none (pass --snapshot for a rollback point)" )

PLAN

if [[ "$CONFIRM" != "yes" ]]; then
  echo "  Dry run. Nothing was changed. Re-run with --yes to apply."
  exit 0
fi

if [[ "$SNAPSHOT" == "yes" ]]; then
  echo "==> snapshot $SNAPNAME"
  pct snapshot "$CTID" "$SNAPNAME" --description "before learnbox update $CURRENT -> $LATEST"
fi

echo "==> updating"
pct exec "$CTID" -- bash "$DIR/scripts/update.sh"

echo
echo "  Done."
if [[ "$SNAPSHOT" == "yes" ]]; then
  cat <<SNAP
  Roll back:        pct rollback $CTID $SNAPNAME
  Delete when happy: pct delsnapshot $CTID $SNAPNAME
  (snapshots older than 14 days raise a monitoring alert)
SNAP
fi
