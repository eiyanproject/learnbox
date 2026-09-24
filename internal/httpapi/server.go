// Package httpapi is the HTTP surface: JSON API, terminal WebSocket, static
// frontend, and the /healthz /readyz /metrics service contract.
package httpapi

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"net"
	"net/http"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"

	"github.com/eiyanproject/learnbox/internal/access"
	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/progress"
	"github.com/eiyanproject/learnbox/internal/runner"
	"github.com/eiyanproject/learnbox/internal/sandbox"
	"github.com/eiyanproject/learnbox/internal/term"
	"github.com/eiyanproject/learnbox/internal/workspace"
)

type Deps struct {
	Version      string
	Commit       string
	Log          *slog.Logger
	Lib          *content.Library
	Sandbox      *sandbox.Sandbox
	Workspace    *workspace.Manager
	Runner       *runner.Runner
	Progress     *progress.Store
	Terms        *term.Manager
	WebDir       string   // built frontend; empty disables static serving
	AllowedHosts []string // besides IP literals and localhost
	MinFreeDisk  int64    // refuse new shells and checks below this much free space

	// AccessHosts are public hostnames served through Cloudflare Access.
	// Requests for them must carry a valid Access token, verified by Access.
	// A nil Access with AccessHosts set refuses those hosts (fail closed).
	AccessHosts []string
	Access      *access.Verifier
}

type Server struct {
	Deps
	mux         *http.ServeMux
	hosts       map[string]bool
	accessHosts map[string]bool

	reqs   *prometheus.CounterVec
	dur    *prometheus.HistogramVec
	errs   *prometheus.CounterVec
	checks *prometheus.CounterVec
	reg    *prometheus.Registry

	toolsMu   sync.Mutex
	tools     map[string]string
	toolsTime time.Time
}

func New(d Deps) *Server {
	s := &Server{Deps: d, mux: http.NewServeMux(), hosts: map[string]bool{"localhost": true}, accessHosts: map[string]bool{}}
	for _, h := range d.AllowedHosts {
		if h = strings.ToLower(strings.TrimSpace(h)); h != "" {
			s.hosts[h] = true
		}
	}
	for _, h := range d.AccessHosts {
		if h = strings.ToLower(strings.TrimSpace(h)); h != "" {
			s.hosts[h] = true
			s.accessHosts[h] = true
		}
	}
	if hn, err := os.Hostname(); err == nil {
		s.hosts[strings.ToLower(hn)] = true
	}

	s.reg = prometheus.NewRegistry()
	s.reg.MustRegister(prometheus.NewGoCollector(), prometheus.NewProcessCollector(prometheus.ProcessCollectorOpts{}))
	buildInfo := prometheus.NewGaugeVec(prometheus.GaugeOpts{Name: "learnbox_build_info", Help: "Running version."}, []string{"version", "commit"})
	buildInfo.WithLabelValues(d.Version, d.Commit).Set(1)
	s.reqs = prometheus.NewCounterVec(prometheus.CounterOpts{Name: "learnbox_requests_total", Help: "HTTP requests."}, []string{"route", "method", "status"})
	s.dur = prometheus.NewHistogramVec(prometheus.HistogramOpts{Name: "learnbox_request_duration_seconds", Help: "HTTP request latency.", Buckets: prometheus.DefBuckets}, []string{"route"})
	s.errs = prometheus.NewCounterVec(prometheus.CounterOpts{Name: "learnbox_errors_total", Help: "Errors by kind."}, []string{"kind"})
	s.checks = prometheus.NewCounterVec(prometheus.CounterOpts{Name: "learnbox_checks_total", Help: "Exercise checks by result."}, []string{"lang", "status"})
	sessions := prometheus.NewGaugeFunc(prometheus.GaugeOpts{Name: "learnbox_terminal_sessions", Help: "Live terminal sessions."}, func() float64 { return float64(d.Terms.Count()) })
	// Both of these are things you want an alert on rather than a discovery:
	// an uncapped learner cgroup looks fine until something spins, and a
	// workspace fills up slowly and then breaks every write at once.
	cpuCapped := prometheus.NewGaugeFunc(prometheus.GaugeOpts{Name: "learnbox_cpu_capped", Help: "1 when the learner cgroup has cpu.max in force."},
		func() float64 {
			if d.Sandbox.CPUCapped() {
				return 1
			}
			return 0
		})
	diskFree := prometheus.NewGaugeFunc(prometheus.GaugeOpts{Name: "learnbox_workspace_free_bytes", Help: "Free space on the learner filesystem."},
		func() float64 {
			free, err := d.Workspace.FreeBytes()
			if err != nil {
				return -1
			}
			return float64(free)
		})
	s.reg.MustRegister(buildInfo, s.reqs, s.dur, s.errs, s.checks, sessions, cpuCapped, diskFree)

	s.routes()
	return s
}

func (s *Server) routes() {
	m := s.mux
	m.HandleFunc("GET /healthz", s.healthz)
	m.HandleFunc("GET /readyz", s.readyz)
	m.Handle("GET /metrics", promhttp.HandlerFor(s.reg, promhttp.HandlerOpts{}))

	m.HandleFunc("GET /api/status", s.status)
	m.HandleFunc("GET /api/tracks", s.tracks)
	const L = "/api/lessons/{lang}/{section}/{slug}"
	m.HandleFunc("GET "+L, s.lesson)
	m.HandleFunc("GET "+L+"/files/{name...}", s.readFile)
	m.HandleFunc("PUT "+L+"/files/{name...}", s.writeFile)
	m.HandleFunc("GET "+L+"/mtimes", s.mtimes)
	m.HandleFunc("POST "+L+"/check", s.check)
	m.HandleFunc("POST "+L+"/hint", s.hint)
	m.HandleFunc("POST "+L+"/reset", s.reset)
	m.HandleFunc("GET /api/term", s.terminal)
	m.HandleFunc("/api/", func(w http.ResponseWriter, r *http.Request) {
		writeErr(w, http.StatusNotFound, "no such endpoint")
	})

	if s.WebDir != "" {
		m.Handle("/", s.static())
	}
}

// Handler wraps the mux with the host guard, CSRF guard, logging and metrics.
func (s *Server) Handler() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		rec := &statusRecorder{ResponseWriter: w, status: 200}

		switch {
		case !s.hostAllowed(r.Host):
			// DNS rebinding: a page on evil.example resolving to this box
			// would otherwise be same-origin with the shell.
			s.errs.WithLabelValues("host_rejected").Inc()
			host := truncate(hostOnly(r.Host), 100)
			s.Log.Warn("host rejected", "host", host)
			writeErr(rec, http.StatusMisdirectedRequest, fmt.Sprintf(
				"unknown host %q; add LAN/Tailscale names to LEARNBOX_ALLOWED_HOSTS, or public names served through Cloudflare Access to LEARNBOX_ACCESS_HOSTS (with LEARNBOX_ACCESS_TEAM_DOMAIN and LEARNBOX_ACCESS_AUD)", host))
		case !s.accessGranted(rec, r):
			// accessGranted wrote the response.
		case r.Method != http.MethodGet && r.Method != http.MethodHead && r.Header.Get("X-Learnbox") != "1":
			// A custom header cannot be sent cross-site without a CORS
			// preflight, which we never approve. Blocks drive-by POSTs.
			s.errs.WithLabelValues("csrf_rejected").Inc()
			writeErr(rec, http.StatusForbidden, "missing X-Learnbox header")
		default:
			s.mux.ServeHTTP(rec, r)
		}

		route := r.Pattern
		if route == "" {
			route = "unmatched"
		}
		d := time.Since(start)
		if route != "GET /api/term" { // websocket: duration is the session length
			s.dur.WithLabelValues(route).Observe(d.Seconds())
		}
		s.reqs.WithLabelValues(route, r.Method, strconv.Itoa(rec.status)).Inc()
		// Log changes and failures; successful reads (the editor polls file
		// mtimes every few seconds) would drown everything else.
		if r.Method != http.MethodGet || rec.status >= 400 {
			lvl := slog.LevelInfo
			if rec.status >= 500 {
				lvl = slog.LevelError
			}
			s.Log.Log(r.Context(), lvl, "request", "route", route, "method", r.Method, "status", rec.status, "dur_ms", d.Milliseconds())
		}
	})
}

// accessGranted enforces Cloudflare Access on public hostnames. Other hosts
// (LAN IPs, Tailscale names) pass straight through.
func (s *Server) accessGranted(w http.ResponseWriter, r *http.Request) bool {
	if !s.accessHosts[hostOnly(r.Host)] {
		return true
	}
	if s.Access == nil {
		s.errs.WithLabelValues("access_unconfigured").Inc()
		writeErr(w, http.StatusServiceUnavailable, "this hostname requires Cloudflare Access verification, which is not configured")
		return false
	}
	email, err := s.Access.Verify(r.Context(), access.TokenFrom(r))
	if err != nil {
		s.errs.WithLabelValues("access_denied").Inc()
		s.Log.Warn("access denied", "host", hostOnly(r.Host), "path", r.URL.Path, "err", err.Error())
		writeErr(w, http.StatusForbidden, "access denied")
		return false
	}
	r.Header.Set("X-Learnbox-User", email)
	return true
}

func truncate(s string, n int) string {
	if len(s) > n {
		return s[:n]
	}
	return s
}

func hostOnly(hostport string) string {
	host := hostport
	if h, _, err := net.SplitHostPort(hostport); err == nil {
		host = h
	}
	return strings.ToLower(strings.Trim(host, "[]"))
}

func (s *Server) hostAllowed(hostport string) bool {
	host := hostOnly(hostport)
	if net.ParseIP(host) != nil {
		return true
	}
	return s.hosts[host]
}

// ---------- contract ----------

func (s *Server) healthz(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok", "version": s.Version})
}

func (s *Server) readyz(w http.ResponseWriter, r *http.Request) {
	problems := []string{}
	if len(s.Lib.Tracks) == 0 {
		problems = append(problems, "no content loaded")
	}
	if _, err := os.Stat(s.Sandbox.Home); err != nil {
		problems = append(problems, "learner home missing")
	}
	if s.tool("python") == "" {
		problems = append(problems, "python not available to learner")
	}
	if err := s.diskHeadroom(); err != nil {
		problems = append(problems, err.Error())
	}
	if len(problems) > 0 {
		writeJSON(w, http.StatusServiceUnavailable, map[string]any{"status": "unavailable", "problems": problems})
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"status": "ready"})
}

// diskHeadroom reports an error when the learner filesystem is nearly full.
// Checks and shells both write there, and a full disk turns every write into a
// failure at once - including the progress file - so it is worth refusing a new
// one with a message that says what is wrong.
func (s *Server) diskHeadroom() error {
	if s.MinFreeDisk <= 0 {
		return nil
	}
	free, err := s.Workspace.FreeBytes()
	if err != nil {
		return nil // statfs failing is not a reason to refuse work
	}
	if free < s.MinFreeDisk {
		return fmt.Errorf("only %d MB free in the workspace (need %d MB); remove something under /home/learner",
			free>>20, s.MinFreeDisk>>20)
	}
	return nil
}

// ---------- status ----------

func (s *Server) status(w http.ResponseWriter, r *http.Request) {
	lessons := 0
	for _, t := range s.Lib.Tracks {
		for _, sec := range t.Sections {
			lessons += len(sec.Lessons)
		}
	}
	writeJSON(w, http.StatusOK, map[string]any{
		"version":       s.Version,
		"tools":         map[string]string{"python": s.tool("python"), "rust": s.tool("rust")},
		"limits_active": s.Sandbox.LimitsActive(),
		"sessions":      s.Terms.Count(),
		"lessons":       lessons,
	})
}

// tool reports the learner's toolchain versions, re-probed at most once a
// minute (rustup may be installed while the service runs).
func (s *Server) tool(name string) string {
	s.toolsMu.Lock()
	defer s.toolsMu.Unlock()
	if s.tools == nil || time.Since(s.toolsTime) > time.Minute {
		s.tools = map[string]string{
			"python": s.probe("python", "--version"),
			"rust":   s.probe("rustc", "--version"),
		}
		s.toolsTime = time.Now()
	}
	return s.tools[name]
}

func (s *Server) probe(name string, args ...string) string {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	var out strings.Builder
	// As the learner: rustup run as root would drop root-owned files into ~/.rustup.
	cmd, err := s.Sandbox.Spawn(func() *exec.Cmd {
		c := exec.CommandContext(ctx, "/bin/sh", append([]string{"-c", `command -v "$0" >/dev/null && exec "$0" "$@"`, name}, args...)...)
		c.Stdout = &out
		return c
	}, (*exec.Cmd).Start)
	if err != nil || cmd.Wait() != nil {
		return ""
	}
	v := strings.TrimSpace(out.String())
	// "Python 3.13.5" -> "3.13.5", "rustc 1.90.0 (1159e78c4 2025-09-14)" -> "1.90.0"
	if f := strings.Fields(v); len(f) >= 2 {
		return f[1]
	}
	return v
}

// ---------- tracks ----------

type lessonSummary struct {
	ID         string `json:"id"`
	Slug       string `json:"slug"`
	Title      string `json:"title"`
	Summary    string `json:"summary"`
	Difficulty int    `json:"difficulty,omitempty"`
	HasTests   bool   `json:"has_tests"`
	Status     string `json:"status"`
}

func (s *Server) tracks(w http.ResponseWriter, r *http.Request) {
	prog, last := s.Progress.All()
	type sectionOut struct {
		ID          string          `json:"id"`
		Title       string          `json:"title"`
		Description string          `json:"description"`
		Lessons     []lessonSummary `json:"lessons"`
		Passed      int             `json:"passed"`
	}
	type trackOut struct {
		Lang        string       `json:"lang"`
		Title       string       `json:"title"`
		Description string       `json:"description"`
		Sections    []sectionOut `json:"sections"`
		Total       int          `json:"total"`
		Passed      int          `json:"passed"`
	}
	out := []trackOut{}
	for _, t := range s.Lib.Tracks {
		to := trackOut{Lang: t.Lang, Title: t.Title, Description: t.Description}
		for _, sec := range t.Sections {
			so := sectionOut{ID: sec.ID, Title: sec.Title, Description: sec.Description, Lessons: []lessonSummary{}}
			for _, l := range sec.Lessons {
				e := prog[l.ID()]
				so.Lessons = append(so.Lessons, lessonSummary{
					ID: l.ID(), Slug: l.Slug, Title: l.Title, Summary: l.Summary,
					Difficulty: l.Difficulty, HasTests: l.HasTest, Status: string(e.Status),
				})
				if e.Status == progress.Passed {
					so.Passed++
				}
			}
			to.Total += len(sec.Lessons)
			to.Passed += so.Passed
			to.Sections = append(to.Sections, so)
		}
		out = append(out, to)
	}
	resp := map[string]any{"tracks": out}
	if l := s.Lib.Lesson(last); l != nil {
		resp["last_lesson"] = map[string]string{"id": l.ID(), "title": l.Title}
	}
	writeJSON(w, http.StatusOK, resp)
}

// ---------- lesson ----------

func (s *Server) lessonFrom(w http.ResponseWriter, r *http.Request) *content.Lesson {
	id := r.PathValue("lang") + "/" + r.PathValue("section") + "/" + r.PathValue("slug")
	l := s.Lib.Lesson(id)
	if l == nil {
		writeErr(w, http.StatusNotFound, "no such lesson")
	}
	return l
}

func (s *Server) lesson(w http.ResponseWriter, r *http.Request) {
	l := s.lessonFrom(w, r)
	if l == nil {
		return
	}
	if _, err := s.Workspace.Ensure(l); err != nil {
		s.fail(w, "workspace", err)
		return
	}
	e, err := s.Progress.Opened(l.ID())
	if err != nil {
		s.fail(w, "progress", err)
		return
	}
	html, err := content.RenderMarkdown(l.Body)
	if err != nil {
		s.fail(w, "markdown", err)
		return
	}
	source := ""
	if l.Source != "" {
		source, _ = content.RenderMarkdown(l.Source)
	}
	var trackTitle, sectionTitle string
	for _, t := range s.Lib.Tracks {
		if t.Lang == l.Lang {
			trackTitle = t.Title
			for _, sec := range t.Sections {
				if sec.ID == l.Section {
					sectionTitle = sec.Title
				}
			}
		}
	}
	link := func(x *content.Lesson) any {
		if x == nil {
			return nil
		}
		return map[string]string{"id": x.ID(), "title": x.Title}
	}
	prev, next := s.Lib.Neighbours(l.ID())
	writeJSON(w, http.StatusOK, map[string]any{
		"id": l.ID(), "lang": l.Lang, "section": l.Section, "slug": l.Slug,
		"title": l.Title, "summary": l.Summary, "html": html, "source_html": source,
		"track_title": trackTitle, "section_title": sectionTitle,
		"files": l.Files, "run": l.Run, "has_tests": l.HasTest,
		"hints_total": len(l.Hints), "hints": renderHints(l.Hints, e.HintsRevealed),
		"status": e.Status, "attempts": e.Attempts,
		"workspace": "~/" + s.Workspace.Rel(l),
		"prev":      link(prev), "next": link(next),
	})
}

func (s *Server) readFile(w http.ResponseWriter, r *http.Request) {
	l := s.lessonFrom(w, r)
	if l == nil {
		return
	}
	f, err := s.Workspace.Read(l, r.PathValue("name"))
	if errors.Is(err, workspace.ErrNotAllowed) {
		writeErr(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		s.fail(w, "workspace", err)
		return
	}
	writeJSON(w, http.StatusOK, f)
}

func (s *Server) writeFile(w http.ResponseWriter, r *http.Request) {
	l := s.lessonFrom(w, r)
	if l == nil {
		return
	}
	var body struct {
		Content string `json:"content"`
	}
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 2<<20)).Decode(&body); err != nil {
		writeErr(w, http.StatusBadRequest, "body must be {\"content\": string}, max 2 MB")
		return
	}
	mtime, err := s.Workspace.Write(l, r.PathValue("name"), body.Content)
	if errors.Is(err, workspace.ErrNotAllowed) {
		writeErr(w, http.StatusNotFound, err.Error())
		return
	}
	if err != nil {
		s.fail(w, "workspace", err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]int64{"mtime": mtime})
}

func (s *Server) mtimes(w http.ResponseWriter, r *http.Request) {
	l := s.lessonFrom(w, r)
	if l == nil {
		return
	}
	writeJSON(w, http.StatusOK, s.Workspace.MTimes(l))
}

func (s *Server) check(w http.ResponseWriter, r *http.Request) {
	l := s.lessonFrom(w, r)
	if l == nil {
		return
	}
	if err := s.diskHeadroom(); err != nil {
		s.errs.WithLabelValues("disk_full").Inc()
		writeErr(w, http.StatusInsufficientStorage, err.Error())
		return
	}
	res, err := s.Runner.Check(r.Context(), l)
	if errors.Is(err, runner.ErrNoTests) {
		writeErr(w, http.StatusBadRequest, err.Error())
		return
	}
	if err != nil {
		s.fail(w, "check", err)
		return
	}
	s.checks.WithLabelValues(l.Lang, res.Status).Inc()
	e, err := s.Progress.Update(l.ID(), func(e *progress.Entry) {
		e.Attempts++
		if res.Passed && e.Status != progress.Passed {
			e.Status = progress.Passed
			e.PassedAt = time.Now().UTC()
		}
	})
	if err != nil {
		s.fail(w, "progress", err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"result": res, "status": e.Status, "attempts": e.Attempts})
}

func (s *Server) hint(w http.ResponseWriter, r *http.Request) {
	l := s.lessonFrom(w, r)
	if l == nil {
		return
	}
	e, err := s.Progress.Update(l.ID(), func(e *progress.Entry) {
		if e.HintsRevealed < len(l.Hints) {
			e.HintsRevealed++
		}
	})
	if err != nil {
		s.fail(w, "progress", err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"hints": renderHints(l.Hints, e.HintsRevealed), "hints_total": len(l.Hints)})
}

func (s *Server) reset(w http.ResponseWriter, r *http.Request) {
	l := s.lessonFrom(w, r)
	if l == nil {
		return
	}
	s.Terms.Kill("lesson/" + l.ID()) // its shell may be sitting in the old directory
	backup, err := s.Workspace.Reset(l)
	if err != nil {
		s.fail(w, "workspace", err)
		return
	}
	resp := map[string]string{"status": "reset"}
	if backup != "" {
		resp["backup"] = "~/" + backup
	}
	writeJSON(w, http.StatusOK, resp)
}

// ---------- helpers ----------

// renderHints returns the first n hints as HTML.
func renderHints(hints []string, n int) []string {
	out := []string{}
	for _, h := range hints[:min(n, len(hints))] {
		html, err := content.RenderMarkdown(h)
		if err != nil {
			html = h
		}
		out = append(out, html)
	}
	return out
}

func (s *Server) fail(w http.ResponseWriter, kind string, err error) {
	s.errs.WithLabelValues(kind).Inc()
	s.Log.Error("request failed", "kind", kind, "err", err.Error())
	writeErr(w, http.StatusInternalServerError, kind+": "+err.Error())
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Cache-Control", "no-store")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

func writeErr(w http.ResponseWriter, status int, msg string) {
	writeJSON(w, status, map[string]string{"error": msg})
}

type statusRecorder struct {
	http.ResponseWriter
	status int
}

func (r *statusRecorder) WriteHeader(code int) {
	r.status = code
	r.ResponseWriter.WriteHeader(code)
}

// Unwrap lets http.ResponseController reach the underlying writer.
func (r *statusRecorder) Unwrap() http.ResponseWriter { return r.ResponseWriter }

// Hijack is needed by the WebSocket upgrade.
func (r *statusRecorder) Hijack() (net.Conn, *bufio.ReadWriter, error) {
	hj, ok := r.ResponseWriter.(http.Hijacker)
	if !ok {
		return nil, nil, errors.New("response writer does not support hijacking")
	}
	r.status = http.StatusSwitchingProtocols
	return hj.Hijack()
}
