#!/usr/bin/env bash
# Installs learnbox inside its LXC. Run as root from the repo checkout
# (normally /opt/learnbox, cloned by create-lxc.sh):
#
#   /opt/learnbox/scripts/install.sh
#
# Idempotent: safe to re-run. update.sh re-runs it after every pull, so
# anything added here reaches existing installs on their next update.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

cd "$(dirname "$0")/.."
ROOT="$PWD"

LEARNER=learner      # owns the workspace and the web shell
APP_USER=learnbox    # runs the Go service (phase 2)
DATA_DIR=/var/lib/learnbox

say() { printf '\n\033[36m==>\033[0m %s\n' "$*"; }
die() { printf '\n\033[31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run as root"

say "Packages"
apt-get update -q
apt-get install -y -q --no-install-recommends \
  ca-certificates curl git less nano vim-tiny procps locales \
  build-essential \
  python3 python3-venv python3-dev

say "Locale"
sed -i 's/^# *en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen
locale-gen >/dev/null
update-locale LANG=en_US.UTF-8

say "Users"
# The learner is a normal login user; the app user has no shell or home.
# Keeping them separate means a stray `rm -rf ~` in the terminal can't
# delete the app, lessons, or progress database.
id "$LEARNER" >/dev/null 2>&1 || useradd --create-home --shell /bin/bash "$LEARNER"
id "$APP_USER" >/dev/null 2>&1 || useradd --system --home-dir "$DATA_DIR" --shell /usr/sbin/nologin "$APP_USER"

# The checkout stays root-owned so neither user can modify the app.
chown -R root:root "$ROOT"
install -d -o "$APP_USER" -g "$APP_USER" -m 0750 "$DATA_DIR"

LHOME="/home/$LEARNER"
install -d -o "$LEARNER" -g "$LEARNER" -m 0755 "$LHOME/learn" "$LHOME/learn/python" "$LHOME/scratch"

say "Python environment for $LEARNER"
if [ ! -x "$LHOME/.venv/bin/python" ]; then
  runuser -u "$LEARNER" -- python3 -m venv "$LHOME/.venv"
fi
runuser -u "$LEARNER" -- "$LHOME/.venv/bin/pip" install -q --upgrade pip pytest

# Activate the venv in every interactive shell, including the web terminal.
MARK="# learnbox: python venv"
if ! grep -qF "$MARK" "$LHOME/.bashrc"; then
  cat >> "$LHOME/.bashrc" <<EOF

$MARK
[ -f "\$HOME/.venv/bin/activate" ] && . "\$HOME/.venv/bin/activate"
cd "\$HOME/learn" 2>/dev/null || true
EOF
fi

# App build and systemd service are added here in phase 2.

say "Verify"
runuser -u "$LEARNER" -- "$LHOME/.venv/bin/python" --version
runuser -u "$LEARNER" -- "$LHOME/.venv/bin/pytest" --version
echo "install OK ($(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo 'no git'))"
