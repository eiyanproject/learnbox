#!/bin/sh
# Regression tests for the Octave shims. Run inside the CT:
#
#   sh /opt/learnbox/lib/octave/tests/run-all.sh
#
# These are not lessons - they are the tests for the library the lessons stand
# on, so a change to string.m or table.m can be checked without working through
# a lesson to find out.
#
# Each file runs in a copy under a temporary directory, because lbx_run writes
# its report into the working directory and /opt/learnbox is mounted read-only
# in some deployments.
set -e
here=$(cd "$(dirname "$0")" && pwd)
lib=$(cd "$here/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp "$here"/test_*.m "$here"/*.csv "$work"/ 2>/dev/null || cp "$here"/test_*.m "$work"/

rc=0
for t in "$work"/test_*.m; do
  name=$(basename "$t" .m)
  out=$(cd "$work" && octave --no-gui --quiet --path "$lib" "$(basename "$t")" 2>&1)
  line=$(echo "$out" | tail -1)
  printf "%-22s %s\n" "$name" "$line"
  case "$line" in
    *", 0 failed") ;;
    *) echo "$out" | grep -A1 "^FAIL" | head -8 | sed 's/^/    /'; rc=1 ;;
  esac
done
echo "EXIT $rc"
exit $rc
