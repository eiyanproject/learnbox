#!/usr/bin/env bash
# Updates the learnbox LXC from the Proxmox host: optional snapshot, then
# brings the container to the latest version.
#
# RUN THIS ON THE PROXMOX HOST. Standalone, like create-lxc.sh:
#
#   curl -fsSLO https://raw.githubusercontent.com/eiyanproject/learnbox/main/scripts/update-lxc.sh
#   bash update-lxc.sh --ctid 116                     # plan only
#   bash update-lxc.sh --ctid 116 --snapshot --yes    # rollback point, then update
#
# Works for every earlier deploy:
#   - a git checkout at /opt/learnbox (create-lxc.sh): pull, rebuild, restart
#   - no checkout (the first deploy/create-ct.sh): clone the repo, full install
#
# Nothing is changed until you pass --yes. Without it you get the plan only.
set -euo pipefail

CTID=""; DIR="/opt/learnbox"; SNAPSHOT="no"; CONFIRM="no"
REPO="https://github.com/eiyanproject/learnbox.git"; BRANCH="main"

die() { echo "error: $*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ctid)     CTID="$2"; shift 2 ;;
    --dir)      DIR="$2"; shift 2 ;;
    --repo)     REPO="$2"; shift 2 ;;
    --branch)   BRANCH="$2"; shift 2 ;;
    --snapshot) SNAPSHOT="yes"; shift ;;
    --yes)      CONFIRM="yes"; shift ;;
    -h|--help)  sed -n '2,15p' "$0"; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

command -v pct >/dev/null || die "pct not found - run this on the Proxmox host"
[[ -n "$CTID" ]] || die "--ctid is required"
pct status "$CTID" &>/dev/null || die "CTID $CTID does not exist on this node (run on the node that hosts it)"
[[ "$(pct status "$CTID")" == "status: running" ]] || die "CTID $CTID is not running"

in_ct() { pct exec "$CTID" -- bash -c "$1"; }

if pct exec "$CTID" -- test -d "$DIR/.git"; then
  MODE="update"
  in_ct "git -C '$DIR' fetch -q origin" 2>/dev/null || true
  CURRENT=$(in_ct "git -C '$DIR' rev-parse --short HEAD" 2>/dev/null || echo "?")
  LATEST=$(in_ct "git -C '$DIR' rev-parse --short '@{u}'" 2>/dev/null || echo "?")
  VERSION_LINE="$CURRENT -> $LATEST"
else
  MODE="migrate"
  VERSION_LINE="no checkout yet -> $BRANCH of $REPO"
fi

if ! pct config "$CTID" | grep -q '^features:.*nesting=1'; then
  NESTING_WARN="  WARNING: nesting=1 is not set. Learner resource limits need it:
           pct set $CTID --features nesting=1 && pct reboot $CTID"
else
  NESTING_WARN=""
fi

SNAPNAME="pre_update_$(date +%Y%m%d_%H%M)"
IP=$(pct exec "$CTID" -- hostname -I 2>/dev/null | awk '{print $1}')

cat <<PLAN

  Plan
  ----
  container     $CTID  ($(pct config "$CTID" | awk '/^hostname:/ {print $2}'), ${IP:-no ip})
  mode          $MODE
  version       $VERSION_LINE
  snapshot      $( [[ "$SNAPSHOT" == "yes" ]] && echo "$SNAPNAME" || echo "none (pass --snapshot for a rollback point)" )
$( [[ "$MODE" == "migrate" ]] && echo "  note          first full install: several minutes (Rust toolchain, build tools, Exercism)" )
$NESTING_WARN

PLAN

if [[ "$CONFIRM" != "yes" ]]; then
  echo "  Dry run. Nothing was changed. Re-run with --yes to apply."
  exit 0
fi

if [[ "$SNAPSHOT" == "yes" ]]; then
  echo "==> snapshot $SNAPNAME"
  pct snapshot "$CTID" "$SNAPNAME" --description "before learnbox update ($VERSION_LINE)"
fi

if [[ "$MODE" == "migrate" ]]; then
  echo "==> cloning $REPO into $DIR"
  in_ct "
    set -e
    export DEBIAN_FRONTEND=noninteractive
    command -v git >/dev/null || { apt-get update -qq && apt-get install -y -qq ca-certificates git >/dev/null; }
    if [ -e '$DIR' ] && [ -n \"\$(ls -A '$DIR' 2>/dev/null)\" ]; then
      mv '$DIR' '$DIR.pre-git.$(date +%s)'
    fi
    rm -rf '$DIR'
    git clone -q --branch '$BRANCH' '$REPO' '$DIR'
  "
  echo "==> installing"
  pct exec "$CTID" -- bash "$DIR/scripts/install.sh"
else
  echo "==> updating"
  pct exec "$CTID" -- bash "$DIR/scripts/update.sh"
fi

echo
echo "  Done. learnbox is at http://${IP:-<ct ip>}:8080"
if [[ "$SNAPSHOT" == "yes" ]]; then
  cat <<SNAP
  Roll back:         pct rollback $CTID $SNAPNAME
  Delete when happy: pct delsnapshot $CTID $SNAPNAME
  (snapshots older than 14 days raise a monitoring alert)
SNAP
fi
