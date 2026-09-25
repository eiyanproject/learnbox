#!/bin/sh
# Regression tests for the Octave shims. Run inside the CT:
#
#   sh /opt/learnbox/lib/octave/tests/run-all.sh
#
# These are not lessons - they are the tests for the library the lessons stand
# on, so a change to string.m or table.m can be checked without working through
# a lesson to find out.
#
# Everything here is copied to a temporary directory first: lbx_run writes its
# report into the working directory, and /opt/learnbox is read-only in some
# deployments. Helper functions live in their own .m files beside the test
# files, so the copy takes all of them, not just test_*.m.
#
# No `set -e`: a failing test file exits nonzero, and aborting on the first one
# would hide the report for every file after it - and the summary line.
here=$(cd "$(dirname "$0")" && pwd)
lib=$(cd "$here/.." && pwd)
work=$(mktemp -d) || exit 1
trap 'rm -rf "$work"' EXIT
cp "$here"/*.m "$work"/ 2>/dev/null
cp "$here"/*.csv "$work"/ 2>/dev/null

rc=0
for t in "$work"/test_*.m; do
  name=$(basename "$t" .m)
  out=$(cd "$work" && octave --no-gui --quiet --norc --path "$lib" "$(basename "$t")" 2>&1)
  line=$(echo "$out" | tail -1)
  printf "%-22s %s\n" "$name" "$line"
  case "$line" in
    *", 0 failed") ;;
    *)
      echo "$out" | grep -A1 "^FAIL" | head -10 | sed 's/^/    /'
      echo "$out" | grep -iE "error|undefined" | head -3 | sed 's/^/    /'
      rc=1
      ;;
  esac
done
echo "EXIT $rc"
exit $rc
