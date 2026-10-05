// learnbox serves the learning platform.
//
//	learnbox serve                                  run the web service (default)
//	learnbox import-exercism <lang> <track-checkout> write Exercism exercises as lessons
//	learnbox verify [id-prefix]                     check every reference solution passes
//
// Configuration is by environment variable; see config() for names and defaults.
package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"path"
	"path/filepath"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/eiyanproject/learnbox/internal/access"
	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/exercism"
	"github.com/eiyanproject/learnbox/internal/httpapi"
	"github.com/eiyanproject/learnbox/internal/profiles"
	"github.com/eiyanproject/learnbox/internal/runner"
	"github.com/eiyanproject/learnbox/internal/sandbox"
	"github.com/eiyanproject/learnbox/internal/term"
	"github.com/eiyanproject/learnbox/internal/workspace"
)

// Set by the build: -ldflags "-X main.version=... -X main.commit=..."
var (
	version = "dev"
	commit  = "unknown"
)

type cfg struct {
	Addr         string
	ContentRoots []string
	ImportRoot   string
	WebDir       string
	DataDir      string
	User         string
	PyLib        string
	JUnitJar     string
	CTestDir     string
	CSharpLib    string
	OctaveDir    string
	Limits       sandbox.Limits
	CheckTimeout time.Duration
	MaxSessions  int
	IdleTimeout  time.Duration
	MinFreeDisk  int64
	AllowedHosts []string
	AccessHosts  []string
	AccessTeam   string
	AccessAUD    string
}

// intEnv and durEnv fall back to the default on anything unparseable. Unlike
// the CPU cap these only tune behaviour, so a typo should not stop the service.
func intEnv(name string, def int) int {
	if n, err := strconv.Atoi(env(name, "")); err == nil && n > 0 {
		return n
	}
	return def
}

func durEnv(name string, def time.Duration) time.Duration {
	if d, err := time.ParseDuration(env(name, "")); err == nil && d > 0 {
		return d
	}
	return def
}

func env(name, def string) string {
	if v, ok := os.LookupEnv(name); ok {
		return v
	}
	return def
}

func config() cfg {
	data := env("LEARNBOX_DATA", "/var/lib/learnbox")
	imported := env("LEARNBOX_IMPORTED", data+"/imported")
	timeout, err := time.ParseDuration(env("LEARNBOX_CHECK_TIMEOUT", "120s"))
	if err != nil {
		timeout = 120 * time.Second
	}
	// A bad value here would silently leave the learner uncapped, so refuse to
	// start instead: the whole point of the setting is that it is in force.
	cpuMax, err := sandbox.ParseCPUMax(env("LEARNBOX_CPU_MAX", "150%"))
	if err != nil {
		fmt.Fprintln(os.Stderr, "LEARNBOX_CPU_MAX:", err)
		os.Exit(2)
	}
	return cfg{
		Addr:         env("LEARNBOX_ADDR", ":8080"),
		ContentRoots: append(strings.Split(env("LEARNBOX_CONTENT", "/opt/learnbox/content"), ","), imported),
		ImportRoot:   imported,
		WebDir:       env("LEARNBOX_WEB", "/opt/learnbox/web/dist"),
		DataDir:      data,
		User:         env("LEARNBOX_USER", "learner"),
		PyLib:        env("LEARNBOX_PYLIB", "/opt/learnbox/lib"),
		JUnitJar:     env("LEARNBOX_JUNIT_JAR", ""),
		CTestDir:     env("LEARNBOX_CTEST_DIR", "/opt/learnbox/lib/ctest"),
		CSharpLib:    env("LEARNBOX_CSHARP_LIB", ""),
		OctaveDir:    env("LEARNBOX_OCTAVE_LIB", ""),
		Limits: sandbox.Limits{
			MemoryMax: env("LEARNBOX_MEMORY_MAX", "1200M"),
			SwapMax:   env("LEARNBOX_SWAP_MAX", "512M"),
			PidsMax:   env("LEARNBOX_PIDS_MAX", "512"),
			CPUMax:    cpuMax,
		},
		MaxSessions:  intEnv("LEARNBOX_MAX_SESSIONS", 8),
		IdleTimeout:  durEnv("LEARNBOX_IDLE_TIMEOUT", 4*time.Hour),
		MinFreeDisk:  int64(intEnv("LEARNBOX_MIN_FREE_MB", 512)) << 20,
		CheckTimeout: timeout,
		AllowedHosts: strings.Split(env("LEARNBOX_ALLOWED_HOSTS", ""), ","),
		AccessHosts:  strings.Split(env("LEARNBOX_ACCESS_HOSTS", ""), ","),
		AccessTeam:   env("LEARNBOX_ACCESS_TEAM_DOMAIN", ""),
		AccessAUD:    env("LEARNBOX_ACCESS_AUD", ""),
	}
}

// newLogger writes one JSON object per line with the service-contract keys
// ts, level, msg, svc.
func newLogger() *slog.Logger {
	h := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
			if len(groups) == 0 {
				switch a.Key {
				case slog.TimeKey:
					a.Key = "ts"
					a.Value = slog.StringValue(a.Value.Time().UTC().Format(time.RFC3339))
				case slog.LevelKey:
					a.Value = slog.StringValue(strings.ToLower(a.Value.String()))
				}
			}
			return a
		},
	})
	return slog.New(h).With("svc", "learnbox")
}

func main() {
	log := newLogger()
	c := config()

	sub := "serve"
	args := os.Args[1:]
	if len(args) > 0 {
		sub, args = args[0], args[1:]
	}

	var err error
	switch sub {
	case "serve":
		err = serve(log, c)
	case "import-exercism":
		err = importExercism(c, args)
	case "verify":
		err = verify(log, c, args)
	case "version":
		fmt.Println(version, commit)
	default:
		err = fmt.Errorf("unknown command %q (serve | import-exercism | verify | version)", sub)
	}
	if err != nil {
		log.Error("fatal", "cmd", sub, "err", err.Error())
		os.Exit(1)
	}
}

// newRunner builds the check runner with the optional Java toolchain attached.
func newRunner(sb *sandbox.Sandbox, ws *workspace.Manager, c cfg) *runner.Runner {
	r := runner.New(sb, ws, c.CheckTimeout)
	r.JUnitJar = c.JUnitJar
	r.CTestDir = c.CTestDir
	r.CSharpLib = c.CSharpLib
	r.OctaveDir = c.OctaveDir
	return r
}

func serve(log *slog.Logger, c cfg) error {
	lib, err := content.Load(c.ContentRoots...)
	if err != nil {
		return fmt.Errorf("load content: %w", err)
	}
	sb, err := sandbox.New(c.User, c.Limits, log)
	if err != nil {
		return err
	}
	sb.PyPath = c.PyLib
	sb.OctPath = c.OctaveDir
	ws, err := workspace.New(sb)
	if err != nil {
		return err
	}
	// The first start creates the default profile around the existing
	// progress.json, so a box upgraded from before profiles loses nothing.
	profs, err := profiles.Open(c.DataDir)
	if err != nil {
		return fmt.Errorf("open profiles: %w", err)
	}
	terms := term.NewManager(sb, log)
	terms.MaxSessions = c.MaxSessions
	terms.IdleTimeout = c.IdleTimeout

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	go terms.Janitor(ctx)

	var verifier *access.Verifier
	accessHosts := strings.Join(c.AccessHosts, "")
	switch {
	case c.AccessTeam != "" && c.AccessAUD != "":
		verifier = access.NewVerifier(c.AccessTeam, c.AccessAUD)
		log.Info("cloudflare access enforced", "hosts", c.AccessHosts, "team", verifier.TeamDomain)
	case accessHosts != "":
		log.Warn("LEARNBOX_ACCESS_HOSTS set without LEARNBOX_ACCESS_TEAM_DOMAIN and LEARNBOX_ACCESS_AUD: those hosts will be refused", "hosts", c.AccessHosts)
	}

	api := httpapi.New(httpapi.Deps{
		Version: version, Commit: commit, Log: log, Lib: lib,
		Sandbox: sb, Workspace: ws, Runner: newRunner(sb, ws, c),
		Profiles: profs, Terms: terms, WebDir: c.WebDir, AllowedHosts: c.AllowedHosts,
		MinFreeDisk: c.MinFreeDisk,
		AccessHosts: c.AccessHosts, Access: verifier,
	})
	srv := &http.Server{Addr: c.Addr, Handler: api.Handler(), ReadHeaderTimeout: 10 * time.Second}

	n := 0
	for _, t := range lib.Tracks {
		for _, s := range t.Sections {
			n += len(s.Lessons)
		}
	}
	log.Info("listening", "addr", c.Addr, "version", version, "tracks", len(lib.Tracks), "lessons", n, "limits", sb.LimitsActive(), "cpu_capped", sb.CPUCapped(),
		"max_sessions", c.MaxSessions, "idle_timeout", c.IdleTimeout.String())

	errc := make(chan error, 1)
	go func() { errc <- srv.ListenAndServe() }()
	select {
	case err := <-errc:
		return err
	case <-ctx.Done():
	}
	log.Info("shutting down")
	shutdown, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(shutdown); err != nil && !errors.Is(err, http.ErrServerClosed) {
		return err
	}
	return nil
}

func importExercism(c cfg, args []string) error {
	if len(args) != 2 {
		return errors.New("usage: learnbox import-exercism <python|rust> <path to exercism track checkout>")
	}
	rep, err := exercism.Import(args[0], args[1], c.ImportRoot)
	if err != nil {
		return err
	}
	fmt.Printf("imported %d %s exercises into %s/%s/practice (%d skipped)\n", rep.Imported, args[0], c.ImportRoot, args[0], len(rep.Skipped))
	for slug, why := range rep.Skipped {
		if why != "deprecated" {
			fmt.Printf("  skipped %-28s %s\n", slug, why)
		}
	}
	return nil
}

// verify copies every reference solution into a scratch workspace and runs
// the lesson's tests against it. A failure means the lesson is broken, not
// the learner.
func verify(log *slog.Logger, c cfg, args []string) error {
	prefix := ""
	if len(args) > 0 {
		prefix = args[0]
	}
	lib, err := content.Load(c.ContentRoots...)
	if err != nil {
		return err
	}
	sb, err := sandbox.New(c.User, sandbox.Limits{}, slog.New(slog.DiscardHandler))
	if err != nil {
		return err
	}
	sb.PyPath = c.PyLib
	sb.OctPath = c.OctaveDir
	ws, err := workspace.New(sb)
	if err != nil {
		return err
	}
	run := newRunner(sb, ws, c)
	// Examples compile one program at a time - a C# lesson can hold several
	// dotnet builds - so they get more time than a single learner Check.
	exRun := newRunner(sb, ws, c)
	exRun.Timeout = max(c.CheckTimeout, 10*time.Minute)

	var failed, checked, skipped int
	for _, t := range lib.Tracks {
		for _, s := range t.Sections {
			for _, l := range s.Lessons {
				if !strings.HasPrefix(l.ID(), prefix) {
					continue
				}
				if !l.HasTest {
					continue
				}
				if _, err := os.Stat(l.SolutionDir()); err != nil {
					skipped++
					continue
				}
				rel := path.Join(".cache/learnbox/verify", l.ID())
				if err := stage(ws, l, rel); err != nil {
					return fmt.Errorf("%s: %w", l.ID(), err)
				}
				res, err := run.CheckDir(context.Background(), l, rel)
				if err != nil {
					return fmt.Errorf("%s: %w", l.ID(), err)
				}
				ws.RemoveAll(rel)
				ex, examples, err := runExamples(exRun, ws, c, l)
				if err != nil {
					return fmt.Errorf("%s: %w", l.ID(), err)
				}
				checked++
				passed := res.Passed && (ex == nil || ex.Passed)
				mark := "ok  "
				if !passed {
					mark = "FAIL"
					failed++
				}
				note := ""
				switch {
				case examples == 1:
					note = " (1 lesson example)"
				case examples > 1:
					note = fmt.Sprintf(" (%d lesson examples)", examples)
				}
				fmt.Printf("%s %-55s %d tests %5dms%s\n", mark, l.ID(), len(res.Tests), res.DurationMS, note)
				if !res.Passed {
					fmt.Println(indent(res.Output))
				}
				if ex != nil && !ex.Passed {
					fmt.Println(indent("lesson examples:\n" + ex.Output))
				}
			}
		}
	}
	fmt.Printf("\n%d checked, %d failed, %d without a reference solution\n", checked, failed, skipped)
	if failed > 0 {
		return fmt.Errorf("%d lessons failed verification", failed)
	}
	return nil
}

// stage puts a fresh copy of a lesson's starter files, overlaid with its
// reference solution, at rel.
func stage(ws *workspace.Manager, l *content.Lesson, rel string) error {
	if err := ws.RemoveAll(rel); err != nil {
		return err
	}
	if err := ws.MkdirAll(rel); err != nil {
		return err
	}
	if err := ws.CopyIn(l.StarterDir(), rel); err != nil && !os.IsNotExist(err) {
		return err
	}
	return ws.CopyIn(l.SolutionDir(), rel)
}

// lessonExamples is what lib/prose/test_lesson_examples.py reads.
type lessonExamples struct {
	Lang     string            `json:"lang"`
	Pycon    []content.Example `json:"pycon"`
	Programs []content.Program `json:"programs"`
	// OctavePath is lib/octave, for MATLAB programs: Octave lacks string,
	// table and the other types it supplies.
	OctavePath string `json:"octave_path"`
}

// programTag is the fence tag of a complete program in a track's lessons.
// The pytest-graded tracks all write Python; the rest write their own language.
func programTag(lang string) string {
	if runner.UsesPytest(lang) {
		return "python"
	}
	return lang
}

// runExamples runs the examples in a lesson's prose, so a claim like "this
// prints 2790" is executed instead of trusted. Two kinds are checked, both
// opted into by their format (see Lesson.Examples and Lesson.Programs):
// ```pycon transcripts, run as doctests, in the Python-based tracks; and in
// every track, a complete program followed by an ```output block, compiled,
// run and compared.
//
// They run beside a copy of the reference solution, so an example may import
// the lesson's own module, and apart from the lesson's tests, so the test
// count stays the real one. It returns nil when the lesson has no examples.
func runExamples(run *runner.Runner, ws *workspace.Manager, c cfg, l *content.Lesson) (*runner.Result, int, error) {
	ex := lessonExamples{Lang: l.Lang, Programs: l.Programs(programTag(l.Lang))}
	if l.Lang == "matlab" {
		ex.OctavePath = c.OctaveDir
		if ex.OctavePath == "" {
			ex.OctavePath = filepath.Join(c.PyLib, "octave")
		}
	}
	if runner.UsesPytest(l.Lang) {
		ex.Pycon = l.Examples("pycon")
	}
	n := len(ex.Pycon) + len(ex.Programs)
	if n == 0 {
		return nil, 0, nil
	}
	rel := path.Join(".cache/learnbox/verify-examples", l.ID())
	if err := stage(ws, l, rel); err != nil {
		return nil, 0, err
	}
	defer ws.RemoveAll(rel)
	raw, err := json.Marshal(ex)
	if err != nil {
		return nil, 0, err
	}
	if err := ws.WriteFileRel(path.Join(rel, "lesson_examples.json"), raw); err != nil {
		return nil, 0, err
	}
	if err := ws.CopyIn(filepath.Join(c.PyLib, "prose"), rel); err != nil {
		return nil, 0, fmt.Errorf("copy the example harness: %w", err)
	}
	res, err := run.PytestDir(context.Background(), rel)
	if err != nil {
		return nil, 0, err
	}
	return res, n, nil
}

func indent(s string) string {
	lines := strings.Split(strings.TrimRight(s, "\n"), "\n")
	if len(lines) > 40 {
		lines = append(lines[:40], "...")
	}
	return "     | " + strings.Join(lines, "\n     | ")
}
