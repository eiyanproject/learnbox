// Package sandbox starts processes as the unprivileged learner user, inside a
// cgroup that caps their memory and process count.
//
// The service itself runs as root. Dropping from uid 0 to a non-zero uid makes
// the kernel clear every capability set, so nothing the learner runs inherits
// privileges. (A non-root service holding ambient capabilities would pass them
// straight through a setuid to the learner.)
package sandbox

import (
	"fmt"
	"log/slog"
	"os"
	"os/exec"
	"os/user"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
)

type Limits struct {
	MemoryMax string // cgroup memory.max, e.g. "1200M"
	SwapMax   string // cgroup memory.swap.max
	PidsMax   string // cgroup pids.max
	CPUMax    string // cgroup cpu.max, e.g. "150000 100000" for 1.5 cores
}

type Sandbox struct {
	User      string
	UID       int
	GID       int
	Home      string
	Path      string // PATH for learner processes
	cgDir     string // learner cgroup directory, "" when unavailable
	cpuCapped bool   // cpu.max is in force on the learner leaf
	cgFD      int    // open fd on cgDir for clone3 placement, -1 when unavailable
	log       *slog.Logger
}

func New(username string, limits Limits, log *slog.Logger) (*Sandbox, error) {
	u, err := user.Lookup(username)
	if err != nil {
		return nil, fmt.Errorf("look up user %q: %w", username, err)
	}
	uid, _ := strconv.Atoi(u.Uid)
	gid, _ := strconv.Atoi(u.Gid)
	s := &Sandbox{
		User: username, UID: uid, GID: gid, Home: u.HomeDir, cgFD: -1, log: log,
		Path: strings.Join([]string{
			filepath.Join(u.HomeDir, ".venv/bin"),
			filepath.Join(u.HomeDir, ".cargo/bin"),
			"/usr/local/bin", "/usr/bin", "/bin",
		}, ":"),
	}
	if limits == (Limits{}) {
		return s, nil // e.g. `learnbox verify` from a shell: leave cgroups alone
	}
	if err := s.setupCgroup(limits); err != nil {
		// Not fatal: the app works without limits, a runaway loop just isn't capped.
		log.Warn("cgroup limits unavailable", "err", err.Error())
	}
	return s, nil
}

// LimitsActive reports whether learner processes are memory/pid capped.
func (s *Sandbox) LimitsActive() bool { return s.cgDir != "" }

// CPUCapped reports whether cpu.max is in force. It is false when the cpu
// controller was not delegated to the container, which readyz surfaces:
// without it a single busy loop can occupy every core the CT has.
func (s *Sandbox) CPUCapped() bool { return s.cpuCapped }

// ParseCPUMax turns a friendly "150%" into the "quota period" pair cgroup v2
// wants, and passes "max" or an already-formatted pair through untouched.
func ParseCPUMax(v string) (string, error) {
	v = strings.TrimSpace(v)
	if v == "" || v == "max" {
		return "max", nil
	}
	if !strings.HasSuffix(v, "%") {
		if _, _, ok := strings.Cut(v, " "); ok {
			return v, nil // "150000 100000", already in cgroup form
		}
		return "", fmt.Errorf("cpu max %q: want a percentage like 150%%, or \"max\"", v)
	}
	pct, err := strconv.Atoi(strings.TrimSuffix(v, "%"))
	if err != nil || pct <= 0 {
		return "", fmt.Errorf("cpu max %q: want a positive percentage like 150%%", v)
	}
	const period = 100000
	return fmt.Sprintf("%d %d", pct*period/100, period), nil
}

func cpuOrNone(enabled bool, v string) string {
	if !enabled {
		return "uncapped (controller unavailable)"
	}
	return v
}

// Env is the environment every learner process starts with.
func (s *Sandbox) Env(extra ...string) []string {
	env := []string{
		"HOME=" + s.Home,
		"USER=" + s.User,
		"LOGNAME=" + s.User,
		"SHELL=/bin/bash",
		"PATH=" + s.Path,
		"LANG=en_US.UTF-8",
		"VIRTUAL_ENV=" + filepath.Join(s.Home, ".venv"),
		"CARGO_HOME=" + filepath.Join(s.Home, ".cargo"),
		"RUSTUP_HOME=" + filepath.Join(s.Home, ".rustup"),
		"PYTHONDONTWRITEBYTECODE=1",
	}
	return append(env, extra...)
}

// LookPath finds an executable on the learner's PATH. exec.Command resolves
// names against the service's own PATH, which does not include the learner's
// venv or cargo, so callers resolve through here first.
func (s *Sandbox) LookPath(name string) (string, error) {
	if strings.Contains(name, "/") {
		return name, nil
	}
	for _, dir := range filepath.SplitList(s.Path) {
		p := filepath.Join(dir, name)
		if st, err := os.Stat(p); err == nil && !st.IsDir() && st.Mode()&0o111 != 0 {
			return p, nil
		}
	}
	return "", fmt.Errorf("%s not found on the learner's PATH (%s)", name, s.Path)
}

// Spawn builds a command with build, turns it into a learner process (uid,
// env, process group, cgroup) and starts it with start - normally cmd.Start,
// or pty.Start for a terminal.
//
// Placing the child straight into the cgroup uses clone3. If a seccomp profile
// refuses that, Spawn rebuilds the command (an exec.Cmd cannot be started
// twice), starts it normally and moves the pid in afterwards.
func (s *Sandbox) Spawn(build func() *exec.Cmd, start func(*exec.Cmd) error) (*exec.Cmd, error) {
	cmd := s.prepare(build())
	err := start(cmd)
	if err == nil || !cmd.SysProcAttr.UseCgroupFD {
		return cmd, err
	}
	s.log.Warn("clone3 cgroup placement refused, falling back to cgroup.procs", "err", err.Error())
	s.cgFD = -1
	cmd = s.prepare(build())
	if err := start(cmd); err != nil {
		return cmd, err
	}
	s.adopt(cmd.Process.Pid)
	return cmd, nil
}

func (s *Sandbox) prepare(cmd *exec.Cmd) *exec.Cmd {
	if cmd.Env == nil {
		cmd.Env = s.Env()
	}
	attr := cmd.SysProcAttr
	if attr == nil {
		attr = &syscall.SysProcAttr{}
		cmd.SysProcAttr = attr
	}
	if os.Geteuid() == 0 {
		attr.Credential = &syscall.Credential{Uid: uint32(s.UID), Gid: uint32(s.GID)}
	}
	if s.cgFD >= 0 {
		attr.UseCgroupFD = true
		attr.CgroupFD = s.cgFD
	}
	return cmd
}

func (s *Sandbox) adopt(pid int) {
	if s.cgDir == "" {
		return
	}
	if err := os.WriteFile(filepath.Join(s.cgDir, "cgroup.procs"), []byte(strconv.Itoa(pid)), 0); err != nil {
		s.log.Warn("move pid into learner cgroup", "pid", pid, "err", err.Error())
	}
}

// Chown gives a path to the learner. No-op when not running as root.
func (s *Sandbox) Chown(path string) error {
	if os.Geteuid() != 0 {
		return nil
	}
	return os.Lchown(path, s.UID, s.GID)
}

// ChownTree gives a whole tree to the learner.
func (s *Sandbox) ChownTree(root string) error {
	if os.Geteuid() != 0 {
		return nil
	}
	return filepath.Walk(root, func(p string, _ os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		return os.Lchown(p, s.UID, s.GID)
	})
}

// setupCgroup expects systemd to have delegated our cgroup (Delegate=yes).
// cgroup v2 forbids processes in a node whose controllers are enabled for its
// children, so the service moves itself into an "app" leaf first, then creates
// a "learner" leaf with the limits.
func (s *Sandbox) setupCgroup(l Limits) error {
	raw, err := os.ReadFile("/proc/self/cgroup")
	if err != nil {
		return err
	}
	line := strings.TrimSpace(string(raw))
	if !strings.HasPrefix(line, "0::") {
		return fmt.Errorf("not on cgroup v2 (%q)", line)
	}
	self := filepath.Join("/sys/fs/cgroup", strings.TrimPrefix(line, "0::"))
	base := self
	if filepath.Base(self) == "app" {
		base = filepath.Dir(self) // restarted inside an existing layout
	}
	app := filepath.Join(base, "app")
	learner := filepath.Join(base, "learner")
	for _, d := range []string{app, learner} {
		if err := os.MkdirAll(d, 0o755); err != nil {
			return err
		}
	}
	if self != app {
		if err := os.WriteFile(filepath.Join(app, "cgroup.procs"), []byte(strconv.Itoa(os.Getpid())), 0); err != nil {
			return fmt.Errorf("move service into app cgroup: %w", err)
		}
	}
	// The cpu controller is often not delegated in an unprivileged LXC. Ask for
	// it, and fall back to memory and pids alone rather than losing those too:
	// a box without a CPU cap is worse than one with no limits at all only if
	// you believed it had one, so the fallback is logged loudly.
	cpuEnabled := true
	if err := os.WriteFile(filepath.Join(base, "cgroup.subtree_control"), []byte("+memory +pids +cpu"), 0); err != nil {
		cpuEnabled = false
		s.log.Warn("cpu controller not delegated; learner CPU is uncapped", "err", err.Error(),
			"fix", "add 'cpu' to the container's delegated controllers, or set CPUAccounting=yes on the unit")
		if err := os.WriteFile(filepath.Join(base, "cgroup.subtree_control"), []byte("+memory +pids"), 0); err != nil {
			return fmt.Errorf("enable memory/pids controllers: %w", err)
		}
	}
	set := func(file, val string) error {
		if val == "" {
			return nil
		}
		if err := os.WriteFile(filepath.Join(learner, file), []byte(val), 0); err != nil {
			return fmt.Errorf("%s=%s: %w", file, val, err)
		}
		return nil
	}
	if err := set("memory.max", l.MemoryMax); err != nil {
		return err
	}
	if err := set("memory.swap.max", l.SwapMax); err != nil {
		s.log.Warn("swap limit not applied", "err", err.Error())
	}
	if err := set("pids.max", l.PidsMax); err != nil {
		return err
	}
	if cpuEnabled {
		// cpu.max bounds a runaway loop; cpu.weight makes the learner yield to
		// the service, so the page still answers while a check is compiling.
		if err := set("cpu.max", l.CPUMax); err != nil {
			s.log.Warn("cpu limit not applied", "err", err.Error())
			cpuEnabled = false
		} else if err := set("cpu.weight", "50"); err != nil {
			s.log.Warn("cpu weight not applied", "err", err.Error())
		}
	}
	fd, err := syscall.Open(learner, syscall.O_DIRECTORY|syscall.O_RDONLY, 0)
	if err != nil {
		return err
	}
	s.cgDir, s.cgFD = learner, fd
	s.cpuCapped = cpuEnabled
	s.log.Info("learner cgroup ready", "path", learner, "memory_max", l.MemoryMax,
		"pids_max", l.PidsMax, "cpu_max", cpuOrNone(cpuEnabled, l.CPUMax))
	return nil
}
