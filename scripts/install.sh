#!/usr/bin/env bash
# Installs learnbox inside its LXC. Run as root from the repo checkout
# (normally /opt/learnbox, cloned by create-lxc.sh):
#
#   /opt/learnbox/scripts/install.sh
#   /opt/learnbox/scripts/install.sh --no-rust       # skip the Rust toolchain
#   /opt/learnbox/scripts/install.sh --no-java       # skip the JDK and JUnit
#   /opt/learnbox/scripts/install.sh --no-exercism   # skip the practice import
#
# Idempotent: safe to re-run. update.sh re-runs it after every pull, so
# anything added here reaches existing installs on their next update.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

cd "$(dirname "$0")/.."
ROOT="$PWD"

WITH_RUST=1
WITH_JAVA=1
WITH_EXERCISM=1
for a in "$@"; do
  case "$a" in
    --no-rust) WITH_RUST=0 ;;
    --no-java) WITH_JAVA=0 ;;
    --no-exercism) WITH_EXERCISM=0 ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
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
# The JUnit console launcher is a single jar, which is why the Java lessons
# need no Maven or Gradle: javac plus this is the whole toolchain.
JUNIT_VERSION=1.11.4
JUNIT_SHA256=b016ef6b1c3454d6d7c2c88ce081dabf289699686af6622d6e4e2e1b54b4a2fc

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
  python3 python3-venv python3-dev \
  iproute2 iputils-ping util-linux

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

# netlab (the CCNA simulator) is shipped on PYTHONPATH rather than pip-installed:
# the repo is root-owned, so an editable install into a learner-owned venv would
# need write access to both. A wrapper puts the console on PATH.
cat > /usr/local/bin/netlab <<NETLAB
#!/bin/sh
exec env PYTHONPATH="$ROOT/lib" "\$HOME/.venv/bin/python" -m netlab "\$@"
NETLAB
chmod 0755 /usr/local/bin/netlab

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

if [ "$WITH_JAVA" -eq 1 ]; then
  say "Java toolchain"
  apt-get install -y -q --no-install-recommends default-jdk-headless
  java -version 2>&1 | head -1
  install -d "$TOOLS/java"
  JUNIT_JAR="$TOOLS/java/junit-platform-console-standalone.jar"
  if [ ! -f "$JUNIT_JAR" ] || ! echo "$JUNIT_SHA256  $JUNIT_JAR" | sha256sum -c --quiet - 2>/dev/null; then
    curl -fsSL "https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/$JUNIT_VERSION/junit-platform-console-standalone-$JUNIT_VERSION.jar"       -o "$JUNIT_JAR.new"
    echo "$JUNIT_SHA256  $JUNIT_JAR.new" | sha256sum -c --quiet - || die "checksum mismatch for the JUnit jar"
    mv "$JUNIT_JAR.new" "$JUNIT_JAR"
  fi
  chmod 0644 "$JUNIT_JAR"
  echo "  junit-platform-console-standalone $JUNIT_VERSION"
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

# Public hostnames served through Cloudflare Access. Requests for these must
# carry a valid Access token, so a shell is never exposed if the edge policy is
# removed. Set all three or none; see docs/REMOTE-ACCESS.md.
# LEARNBOX_ACCESS_HOSTS=learnbox.eiyanproject.com
# LEARNBOX_ACCESS_TEAM_DOMAIN=<team>.cloudflareaccess.com
# LEARNBOX_ACCESS_AUD=<application audience tag>
LEARNBOX_ACCESS_HOSTS=
LEARNBOX_ACCESS_TEAM_DOMAIN=
LEARNBOX_ACCESS_AUD=

# Limits for everything the learner runs (terminals and checks, combined).
# CPU_MAX is a percentage of one core: 150% is 1.5 of the CT's 2 vCPUs, which
# leaves the service responsive while a check compiles.
LEARNBOX_MEMORY_MAX=1200M
LEARNBOX_SWAP_MAX=512M
LEARNBOX_PIDS_MAX=512
LEARNBOX_CPU_MAX=150%
LEARNBOX_CHECK_TIMEOUT=120s

# Terminal sessions. Detached sessions are killed after IDLE_TIMEOUT; the
# oldest detached one is evicted when MAX_SESSIONS is reached.
LEARNBOX_MAX_SESSIONS=8
LEARNBOX_IDLE_TIMEOUT=4h

# Refuse new shells and checks below this much free space, so a full workspace
# fails with a message instead of breaking every write at once.
LEARNBOX_MIN_FREE_MB=512
EOF
fi

# Existing installs keep their settings; add newly introduced keys they lack.
if ! grep -q "^LEARNBOX_ACCESS_HOSTS=" /etc/learnbox.env; then
  cat >> /etc/learnbox.env <<'ENVEOF'

# Public hostnames served through Cloudflare Access. Requests for these must
# carry a valid Access token, so a shell is never exposed if the edge policy is
# removed. Set all three or none; see docs/REMOTE-ACCESS.md.
LEARNBOX_ACCESS_HOSTS=
LEARNBOX_ACCESS_TEAM_DOMAIN=
LEARNBOX_ACCESS_AUD=
ENVEOF
  echo "  added Cloudflare Access settings to /etc/learnbox.env"
fi

# Same for the resource caps: an install that predates them would otherwise
# keep running with no CPU limit and no disk floor.
if ! grep -q "^LEARNBOX_CPU_MAX=" /etc/learnbox.env; then
  cat >> /etc/learnbox.env <<'ENVEOF'

# CPU cap for everything the learner runs, as a percentage of one core.
LEARNBOX_CPU_MAX=150%
# Terminal sessions: oldest detached one is evicted at MAX_SESSIONS.
LEARNBOX_MAX_SESSIONS=8
LEARNBOX_IDLE_TIMEOUT=4h
# Refuse new shells and checks below this much free space.
LEARNBOX_MIN_FREE_MB=512
ENVEOF
  echo "  added CPU, session and disk limits to /etc/learnbox.env"
fi

# The env file holds the Access audience tag; keep it off other accounts.
chown root:root /etc/learnbox.env
chmod 600 /etc/learnbox.env

# Values handed in through the environment (update-lxc.sh --access-*) are
# written into the env file, so a deploy can configure Access without anyone
# hand-editing a file on the container. Unset variables change nothing.
if [ -n "${LEARNBOX_ACCESS_HOSTS:-}${LEARNBOX_ACCESS_TEAM_DOMAIN:-}${LEARNBOX_ACCESS_AUD:-}" ]; then
  [ -n "${LEARNBOX_ACCESS_HOSTS:-}" ] && [ -n "${LEARNBOX_ACCESS_TEAM_DOMAIN:-}" ] &&
    [ -n "${LEARNBOX_ACCESS_AUD:-}" ] ||
    die "set all three of LEARNBOX_ACCESS_HOSTS, LEARNBOX_ACCESS_TEAM_DOMAIN and LEARNBOX_ACCESS_AUD, or none: two of three fails closed and the hostname stops working"

  # Accept a pasted "https://team.cloudflareaccess.com/" as well as the bare name.
  team=${LEARNBOX_ACCESS_TEAM_DOMAIN#https://}
  team=${team%/}
  case "$team" in
    *.cloudflareaccess.com) ;;
    *) die "LEARNBOX_ACCESS_TEAM_DOMAIN should be the full team domain, e.g. yourteam.cloudflareaccess.com (got '$team')" ;;
  esac
  case "$LEARNBOX_ACCESS_AUD" in
    *[!0-9a-f]* | "") echo "  warning: audience tag is not the usual 64 hex characters - check you copied the AUD tag, not the app id" ;;
  esac

  set_env_key() {
    awk -v k="$1" -v v="$2" '
      $0 ~ "^" k "=" && !done { print k "=" v; done = 1; next }
      { print }
      END { if (!done) print k "=" v }
    ' /etc/learnbox.env > /etc/learnbox.env.new
    cat /etc/learnbox.env.new > /etc/learnbox.env   # keep the original mode
    rm -f /etc/learnbox.env.new
  }
  set_env_key LEARNBOX_ACCESS_HOSTS "$LEARNBOX_ACCESS_HOSTS"
  set_env_key LEARNBOX_ACCESS_TEAM_DOMAIN "$team"
  set_env_key LEARNBOX_ACCESS_AUD "$LEARNBOX_ACCESS_AUD"
  echo "  Cloudflare Access enforced for: $LEARNBOX_ACCESS_HOSTS (team $team)"
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
Environment=LEARNBOX_PYLIB=$ROOT/lib
Environment=LEARNBOX_JUNIT_JAR=$TOOLS/java/junit-platform-console-standalone.jar
WorkingDirectory=$DATA_DIR
# The service manages its own cgroup subtree: an app leaf for itself and a
# learner leaf with memory/pid/cpu limits for shells and checks.
Delegate=yes
KillMode=control-group
Restart=on-failure
RestartSec=2
# A learner process hitting its own memory.max is a normal event - the default
# OOMPolicy would stop learnbox itself when that happens.
OOMPolicy=continue
# Backstop under the per-learner cgroup caps, in case the learner leaf could
# not be created. Leaves headroom on a 2 vCPU CT so the UI still answers.
CPUAccounting=yes
MemoryAccounting=yes
TasksAccounting=yes
CPUQuota=180%
TasksMax=1024
# Do not hot-loop on a config error: five failures in five minutes is enough.
StartLimitIntervalSec=300
StartLimitBurst=5

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
