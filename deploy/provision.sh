#!/usr/bin/env bash
# Run INSIDE the learnbox CT as root. Safe to re-run.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

LEARNER=learner      # owns the workspace and the web shell
APP_USER=learnbox    # runs the Go service (phase 2)
APP_DIR=/opt/learnbox
DATA_DIR=/var/lib/learnbox

echo "==> Packages"
apt-get update -q
apt-get install -y -q --no-install-recommends \
  ca-certificates curl git less nano vim-tiny procps locales \
  build-essential \
  python3 python3-venv python3-dev

echo "==> Locale"
sed -i 's/^# *en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen
locale-gen >/dev/null
update-locale LANG=en_US.UTF-8

echo "==> Users"
# The learner is a normal login user; the app user has no shell or home.
# Keeping them separate means a stray `rm -rf ~` in the terminal can't
# delete the app binary, lessons, or progress database.
id "$LEARNER" >/dev/null 2>&1 || useradd --create-home --shell /bin/bash "$LEARNER"
id "$APP_USER" >/dev/null 2>&1 || useradd --system --home-dir "$DATA_DIR" --shell /usr/sbin/nologin "$APP_USER"

install -d -o root      -g root      -m 0755 "$APP_DIR"
install -d -o "$APP_USER" -g "$APP_USER" -m 0750 "$DATA_DIR"

LHOME="/home/$LEARNER"
install -d -o "$LEARNER" -g "$LEARNER" -m 0755 "$LHOME/learn" "$LHOME/learn/python" "$LHOME/scratch"

echo "==> Python environment for $LEARNER"
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

echo "==> Verify"
runuser -u "$LEARNER" -- bash -ic 'python --version && pytest --version' 2>/dev/null
echo "provision OK"
