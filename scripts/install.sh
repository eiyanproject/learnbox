#!/usr/bin/env bash
# Installs learnbox inside its LXC. Run as root from the repo checkout
# (normally /opt/learnbox, cloned by create-lxc.sh):
#
#   /opt/learnbox/scripts/install.sh
#   /opt/learnbox/scripts/install.sh --no-rust       # skip the Rust toolchain
#   /opt/learnbox/scripts/install.sh --no-exercism   # skip the practice import
#
# Idempotent: safe to re-run. update.sh re-runs it after every pull, so
# anything added here reaches existing installs on their next update.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

cd "$(dirname "$0")/.."
ROOT="$PWD"

WITH_RUST=1
WITH_EXERCISM=1
for a in "$@"; do
  case "$a" in
    --no-rust) WITH_RUST=0 ;;
    --no-exercism) WITH_EXERCISM=0 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done

LEARNER=learner
DATA_DIR=/var/lib/learnbox
TOOLS=/opt/learnbox-toolchain       # build-only toolchains, outside the checkout
CACHE=/var/cache/learnbox-build

# Pinned build toolchains. Bump deliberately; the checksums come from
# https://go.dev/dl/?mode=json and https://nodejs.org/dist/<v>/SHASUMS256.txt
GO_VERSION=1.26.8
GO_SHA256=d0f743b33e8d8945e6b1f432edd15785c70507121d6e2a723b21285eddf8b57b
NODE_VERSION=v24.21.0
NODE_SHA256=6e1db87ef58b8819e5d5402eff1536491b18edd8eb7bee5ef7897876e88dc5ff

as_learner() { runuser -u "$LEARNER" -- env HOME="/home/$LEARNER" USER="$LEARNER" LOGNAME="$LEARNER" "$@"; }
say() { printf '\n\033[36m==>\033[0m %s\n' "$*"; }
die() { printf '\n\033[31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run as root"
[ "$(uname -m)" = "x86_64" ] || die "only x86_64 is supported (pinned toolchain downloads)"

# ---------------------------------------------------------------- system
say "Packages"
apt-get update -q
apt-get install -y -q --no-install-recommends \
  ca-certificates curl git less nano vim-tiny procps locales tmux \
  build-essential pkg-config \
  python3 python3-venv python3-dev

say "Locale"
sed -i 's/^# *en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen
locale-gen >/dev/null
update-locale LANG=en_US.UTF-8

say "Learner user"
# The learner owns the workspace and every shell the web terminal opens. The
# service runs as root and drops to this user for anything it starts, so a
# stray `rm -rf ~` in the terminal cannot touch the app, lessons, or progress.
id "$LEARNER" >/dev/null 2>&1 || useradd --create-home --shell /bin/bash "$LEARNER"
LHOME="/home/$LEARNER"
install -d -o "$LEARNER" -g "$LEARNER" -m 0755 "$LHOME/learn" "$LHOME/scratch" "$LHOME/.cache"
install -d -o root -g root -m 0750 "$DATA_DIR"
chown -R root:root "$ROOT"

say "Cleaning up earlier versions"
# The first deploy (deploy/provision.sh) added a .bashrc block that cd'd into
# ~/learn, which would pull every lesson terminal out of its workspace, and a
# `learnbox` system user the service no longer uses.
if grep -qF "# learnbox: python venv" "$LHOME/.bashrc"; then
  sed -i '/^# learnbox: python venv$/,/^cd "\$HOME\/learn" 2>\/dev\/null || true$/d' "$LHOME/.bashrc"
  echo "  removed old .bashrc block"
fi
if id learnbox >/dev/null 2>&1 && ! pgrep -u learnbox >/dev/null 2>&1; then
  userdel learnbox && echo "  removed unused learnbox user"
fi
chown root:root "$DATA_DIR"

say "Python environment for $LEARNER"
if [ ! -x "$LHOME/.venv/bin/python" ]; then
  as_learner python3 -m venv "$LHOME/.venv"
fi
as_learner "$LHOME/.venv/bin/pip" install -q --upgrade pip pytest

MARK="# learnbox: environment"
if ! grep -qF "$MARK" "$LHOME/.bashrc"; then
  cat >> "$LHOME/.bashrc" <<'EOF'

# learnbox: environment
[ -f "$HOME/.venv/bin/activate" ] && . "$HOME/.venv/bin/activate"
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
EOF
fi

if [ "$WITH_RUST" -eq 1 ]; then
  say "Rust toolchain for $LEARNER"
  if [ ! -x "$LHOME/.cargo/bin/cargo" ]; then
    curl -fsSL https://sh.rustup.rs -o /tmp/rustup-init.sh
    as_learner sh /tmp/rustup-init.sh -y --no-modify-path --profile minimal \
      --component clippy,rustfmt
    rm -f /tmp/rustup-init.sh
  fi
  as_learner "$LHOME/.cargo/bin/rustc" --version
fi

# ---------------------------------------------------------------- build tools
fetch() { # url sha256 dest
  curl -fsSL "$1" -o "$3"
  echo "$2  $3" | sha256sum -c --quiet - || die "checksum mismatch for $1"
}

say "Go $GO_VERSION (build only)"
install -d "$TOOLS" "$CACHE"
if [ "$("$TOOLS/go/bin/go" env GOVERSION 2>/dev/null)" != "go$GO_VERSION" ]; then
  fetch "https://go.dev/dl/go$GO_VERSION.linux-amd64.tar.gz" "$GO_SHA256" /tmp/go.tgz
  rm -rf "$TOOLS/go"
  tar -C "$TOOLS" -xzf /tmp/go.tgz
  rm /tmp/go.tgz
fi

say "Node $NODE_VERSION (build only)"
if [ "$("$TOOLS/node/bin/node" --version 2>/dev/null)" != "$NODE_VERSION" ]; then
  fetch "https://nodejs.org/dist/$NODE_VERSION/node-$NODE_VERSION-linux-x64.tar.gz" "$NODE_SHA256" /tmp/node.tgz
  rm -rf "$TOOLS/node"
  mkdir -p "$TOOLS/node"
  tar -C "$TOOLS/node" --strip-components=1 -xzf /tmp/node.tgz
  rm /tmp/node.tgz
fi

# ---------------------------------------------------------------- build
VERSION=$(git -C "$ROOT" describe --tags --always --dirty 2>/dev/null || echo dev)
COMMIT=$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)

say "Building server ($VERSION)"
install -d "$ROOT/bin"
(
  export PATH="$TOOLS/go/bin:$PATH" GOTOOLCHAIN=local GOPATH="$CACHE/gopath" GOCACHE="$CACHE/gocache" CGO_ENABLED=0
  go build -trimpath -ldflags "-s -w -X main.version=$VERSION -X main.commit=$COMMIT" \
    -o "$ROOT/bin/learnbox.new" ./cmd/learnbox
)
mv "$ROOT/bin/learnbox.new" "$ROOT/bin/learnbox"

say "Building frontend"
(
  export PATH="$TOOLS/node/bin:$PATH" npm_config_cache="$CACHE/npm"
  cd "$ROOT/web"
  npm ci --no-audit --no-fund --loglevel=error
  npm run build --silent
)

# ---------------------------------------------------------------- practice
if [ "$WITH_EXERCISM" -eq 1 ]; then
  say "Exercism practice exercises"
  install -d "$DATA_DIR/sources"
  for lang in python rust; do
    [ "$lang" = rust ] && [ "$WITH_RUST" -eq 0 ] && continue
    src="$DATA_DIR/sources/$lang"
    if [ -d "$src/.git" ]; then
      git -C "$src" fetch -q --depth 1 origin main && git -C "$src" reset -q --hard origin/main
    else
      git clone -q --depth 1 "https://github.com/exercism/$lang.git" "$src"
    fi
    LEARNBOX_DATA="$DATA_DIR" "$ROOT/bin/learnbox" import-exercism "$lang" "$src" | sed -n 1p
  done
fi

# ---------------------------------------------------------------- service
say "Service"
if [ ! -f /etc/learnbox.env ]; then
  cat > /etc/learnbox.env <<'EOF'
# learnbox settings. Restart after changes: systemctl restart learnbox
LEARNBOX_ADDR=:8080

# Hostnames you open learnbox by, besides IP addresses and localhost.
# Requests for any other name are refused (DNS-rebinding protection).
# Example: LEARNBOX_ALLOWED_HOSTS=learnbox,learnbox.lan,learnbox.tail1234.ts.net
LEARNBOX_ALLOWED_HOSTS=

# Limits for everything the learner runs (terminals and checks, combined).
LEARNBOX_MEMORY_MAX=1200M
LEARNBOX_SWAP_MAX=512M
LEARNBOX_PIDS_MAX=512
LEARNBOX_CHECK_TIMEOUT=120s
EOF
fi

cat > /etc/systemd/system/learnbox.service <<EOF
[Unit]
Description=learnbox learning platform
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=$ROOT/bin/learnbox serve
EnvironmentFile=-/etc/learnbox.env
Environment=LEARNBOX_CONTENT=$ROOT/content
Environment=LEARNBOX_WEB=$ROOT/web/dist
Environment=LEARNBOX_DATA=$DATA_DIR
WorkingDirectory=$DATA_DIR
# The service manages its own cgroup subtree: an app leaf for itself and a
# learner leaf with memory/pid limits for shells and checks.
Delegate=yes
KillMode=control-group
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

if [ -d /run/systemd/system ]; then
  systemctl daemon-reload
  systemctl enable -q learnbox
  systemctl restart learnbox
  port=$(sed -n 's/^LEARNBOX_ADDR=.*:\([0-9]*\)$/\1/p' /etc/learnbox.env | tail -1)
  port=${port:-8080}
  for _ in $(seq 1 20); do
    curl -fsS "http://127.0.0.1:$port/healthz" >/dev/null 2>&1 && break
    sleep 1
  done
  curl -fsS "http://127.0.0.1:$port/healthz" >/dev/null || die "service did not come up: journalctl -u learnbox -n 50"
  curl -fsS "http://127.0.0.1:$port/readyz" || true
  echo
  echo "install OK ($VERSION): http://$(hostname -I | awk '{print $1}'):$port"
else
  echo "systemd is not running here; start manually: $ROOT/bin/learnbox serve"
fi
