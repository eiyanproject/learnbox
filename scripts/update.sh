#!/usr/bin/env bash
# Updates an existing install: pull, then re-run install.sh. Run as root
# inside the LXC:
#
#   /opt/learnbox/scripts/update.sh
#   /opt/learnbox/scripts/update.sh --no-pull   # re-apply the working tree as-is
#
# Your workspace (/home/learner) and progress (/var/lib/learnbox) are never
# touched by an update.
set -euo pipefail

# Everything is inside main() so bash parses the whole file before running
# any of it - `git pull` may rewrite this very script mid-run.
main() {
cd "$(dirname "$0")/.."
ROOT="$PWD"
PULL=1

for a in "$@"; do
  case "$a" in
    --no-pull) PULL=0 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done

say() { printf '\n\033[36m==>\033[0m %s\n' "$*"; }
die() { printf '\n\033[31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run as root"
git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1 || die "$ROOT is not a git checkout"

BEFORE=$(git rev-parse --short HEAD)

if [ "$PULL" -eq 1 ]; then
  say "Pulling"
  [ -z "$(git status --porcelain)" ] || die "working tree is dirty. Commit, stash, or re-run with --no-pull."
  git pull --ff-only
fi

AFTER=$(git rev-parse --short HEAD)
if [ "$BEFORE" = "$AFTER" ]; then
  echo "  already at $AFTER"
else
  echo "  $BEFORE -> $AFTER"
  git --no-pager log --oneline "$BEFORE..$AFTER"
fi

# Re-exec the freshly pulled install.sh, not the copy bash already has open.
exec "$ROOT/scripts/install.sh"
}

main "$@"
