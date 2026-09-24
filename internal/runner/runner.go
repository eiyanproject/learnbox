// Package runner checks a lesson: it copies the learner's workspace plus the
// hidden tests into a scratch directory and runs the language's test tool
// there as the learner.
package runner

import (
	"bytes"
	"context"
	"encoding/xml"
	"errors"
	"fmt"
	"os/exec"
	"path"
	"regexp"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/sandbox"
	"github.com/eiyanproject/learnbox/internal/workspace"
)

const maxOutput = 128 << 10

type TestResult struct {
	Name    string `json:"name"`
	Passed  bool   `json:"passed"`
	Message string `json:"message,omitempty"`
}

type Result struct {
	Status     string       `json:"status"` // passed | failed | error | timeout
	Passed     bool         `json:"passed"`
	Tests      []TestResult `json:"tests"`
	Output     string       `json:"output"`
	DurationMS int64        `json:"duration_ms"`
}

type Runner struct {
	sb      *sandbox.Sandbox
	ws      *workspace.Manager
	Timeout time.Duration
	mu      sync.Mutex // one check at a time: compiles are the RAM spike
}

func New(sb *sandbox.Sandbox, ws *workspace.Manager, timeout time.Duration) *Runner {
	return &Runner{sb: sb, ws: ws, Timeout: timeout}
}

var ErrNoTests = errors.New("lesson has no tests")

// Check runs the hidden tests against the learner's current workspace.
func (r *Runner) Check(ctx context.Context, l *content.Lesson) (*Result, error) {
	return r.check(ctx, l, "")
}

// CheckDir runs the hidden tests against files in srcRel (relative to the
// learner's home) instead of the workspace. Used by `learnbox verify`.
func (r *Runner) CheckDir(ctx context.Context, l *content.Lesson, srcRel string) (*Result, error) {
	return r.check(ctx, l, srcRel)
}

func (r *Runner) check(ctx context.Context, l *content.Lesson, srcRel string) (*Result, error) {
	if !l.HasTest {
		return nil, ErrNoTests
	}
	r.mu.Lock()
	defer r.mu.Unlock()

	if srcRel == "" {
		if _, err := r.ws.Ensure(l); err != nil {
			return nil, err
		}
		srcRel = r.ws.Rel(l)
	}
	checkRel := path.Join(".cache/learnbox/check", l.Lang, l.Section, l.Slug)
	if err := r.ws.RemoveAll(checkRel); err != nil {
		return nil, err
	}
	if err := r.ws.MkdirAll(checkRel); err != nil {
		return nil, err
	}
	if err := r.ws.CopyWithin(srcRel, checkRel); err != nil {
		return nil, fmt.Errorf("copy workspace: %w", err)
	}
	checkDir := r.sb.Home + "/" + checkRel

	switch l.Lang {
	// CCNA lessons are graded by pytest as well: the learner edits IOS config
	// files, and the tests apply them to the simulator and assert the network
	// actually forwards. Same runner, different thing being written.
	case "python", "ccna":
		if err := r.ws.CopyIn(l.TestsDir(), checkRel); err != nil {
			return nil, fmt.Errorf("copy tests: %w", err)
		}
		return r.python(ctx, checkRel, checkDir)
	case "rust":
		if err := r.ws.CopyIn(l.TestsDir(), checkRel+"/tests"); err != nil {
			return nil, fmt.Errorf("copy tests: %w", err)
		}
		return r.rust(ctx, checkDir)
	default:
		return nil, fmt.Errorf("no checker for language %q", l.Lang)
	}
}

func (r *Runner) exec(ctx context.Context, dir string, env []string, name string, args ...string) (out string, exitCode int, timedOut bool, dur time.Duration, err error) {
	ctx, cancel := context.WithTimeout(ctx, r.Timeout)
	defer cancel()

	bin, err := r.sb.LookPath(name)
	if err != nil {
		return "", 0, false, 0, err
	}
	var buf limitedBuffer
	start := time.Now()
	cmd, err := r.sb.Spawn(func() *exec.Cmd {
		c := exec.Command(bin, args...)
		c.Dir = dir
		c.Env = r.sb.Env(env...)
		c.Stdout, c.Stderr = &buf, &buf
		c.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
		return c
	}, (*exec.Cmd).Start)
	if err != nil {
		return "", 0, false, 0, err
	}
	done := make(chan error, 1)
	go func() { done <- cmd.Wait() }()

	select {
	case err = <-done:
	case <-ctx.Done():
		syscall.Kill(-cmd.Process.Pid, syscall.SIGKILL) // whole group: cargo spawns rustc
		err = <-done
		timedOut = true
	}
	dur = time.Since(start)
	var exitErr *exec.ExitError
	if errors.As(err, &exitErr) {
		return buf.String(), exitErr.ExitCode(), timedOut, dur, nil
	}
	return buf.String(), 0, timedOut, dur, err
}

// ---------- python ----------

func (r *Runner) python(ctx context.Context, checkRel, dir string) (*Result, error) {
	const report = ".learnbox-report.xml"
	out, code, timedOut, dur, err := r.exec(ctx, dir, nil,
		"python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--color=no",
		"--junitxml="+report, "-o", "junit_family=xunit1")
	if err != nil {
		return nil, err
	}
	res := &Result{Output: out, DurationMS: dur.Milliseconds()}
	if timedOut {
		res.Status = "timeout"
		return res, nil
	}
	if raw, err := r.ws.ReadFileRel(path.Join(checkRel, report)); err == nil {
		res.Tests = parseJUnit(raw)
	}
	finish(res, code)
	return res, nil
}

type junitSuites struct {
	Suites []junitSuite `xml:"testsuite"`
}
type junitSuite struct {
	Cases []junitCase `xml:"testcase"`
}
type junitCase struct {
	Name    string      `xml:"name,attr"`
	Class   string      `xml:"classname,attr"`
	Failure *junitIssue `xml:"failure"`
	Error   *junitIssue `xml:"error"`
	Skipped *junitIssue `xml:"skipped"`
}
type junitIssue struct {
	Message string `xml:"message,attr"`
	Body    string `xml:",chardata"`
}

func parseJUnit(raw []byte) []TestResult {
	var doc junitSuites
	if err := xml.Unmarshal(raw, &doc); err != nil || len(doc.Suites) == 0 {
		var one junitSuite
		if xml.Unmarshal(raw, &one) != nil {
			return nil
		}
		doc.Suites = []junitSuite{one}
	}
	var tests []TestResult
	for _, s := range doc.Suites {
		for _, c := range s.Cases {
			if c.Skipped != nil {
				continue
			}
			t := TestResult{Name: prettyTestName(c.Name), Passed: true}
			for _, issue := range []*junitIssue{c.Failure, c.Error} {
				if issue != nil {
					t.Passed = false
					t.Message = pythonMessage(issue)
				}
			}
			tests = append(tests, t)
		}
	}
	return tests
}

func prettyTestName(n string) string {
	n = strings.TrimPrefix(n, "test_")
	return strings.ReplaceAll(n, "_", " ")
}

// pythonMessage keeps the assertion line, not the whole traceback.
func pythonMessage(i *junitIssue) string {
	var keep []string
	for _, line := range strings.Split(i.Body, "\n") {
		if strings.HasPrefix(line, "E ") {
			keep = append(keep, strings.TrimSpace(strings.TrimPrefix(line, "E ")))
		}
	}
	if len(keep) > 0 {
		if len(keep) > 6 {
			keep = keep[:6]
		}
		return strings.Join(keep, "\n")
	}
	return i.Message
}

// ---------- rust ----------

var (
	rustTestLine = regexp.MustCompile(`(?m)^test (\S+) \.\.\. (ok|FAILED|ignored)`)
	rustSection  = regexp.MustCompile(`(?m)^---- (\S+) stdout ----$`)
)

func (r *Runner) rust(ctx context.Context, dir string) (*Result, error) {
	out, code, timedOut, dur, err := r.exec(ctx, dir,
		[]string{
			"CARGO_TARGET_DIR=" + r.sb.Home + "/.cache/learnbox/target",
			"CARGO_TERM_COLOR=never",
		},
		"cargo", "test", "--no-fail-fast", "--", "--include-ignored", "--test-threads=1", "--color=never")
	if err != nil {
		return nil, err
	}
	res := &Result{Output: out, DurationMS: dur.Milliseconds()}
	if timedOut {
		res.Status = "timeout"
		return res, nil
	}
	msgs := rustFailureMessages(out)
	seen := map[string]bool{}
	for _, m := range rustTestLine.FindAllStringSubmatch(out, -1) {
		name, status := m[1], m[2]
		if status == "ignored" || seen[name] {
			continue
		}
		seen[name] = true
		res.Tests = append(res.Tests, TestResult{
			Name: prettyTestName(name), Passed: status == "ok", Message: msgs[name],
		})
	}
	finish(res, code)
	return res, nil
}

func rustFailureMessages(out string) map[string]string {
	msgs := map[string]string{}
	locs := rustSection.FindAllStringSubmatchIndex(out, -1)
	for i, loc := range locs {
		name := out[loc[2]:loc[3]]
		end := len(out)
		if i+1 < len(locs) {
			end = locs[i+1][0]
		}
		body := out[loc[1]:end]
		if j := strings.Index(body, "\nfailures:"); j >= 0 {
			body = body[:j]
		}
		var keep []string
		for _, line := range strings.Split(strings.TrimSpace(body), "\n") {
			if strings.HasPrefix(line, "note: run with `RUST_BACKTRACE") {
				continue
			}
			keep = append(keep, line)
		}
		msgs[name] = strings.Join(keep, "\n")
	}
	return msgs
}

// ---------- shared ----------

func finish(res *Result, exitCode int) {
	failed := 0
	for _, t := range res.Tests {
		if !t.Passed {
			failed++
		}
	}
	switch {
	case len(res.Tests) == 0:
		res.Status = "error" // did not compile, import failed, syntax error...
	case failed > 0 || exitCode != 0:
		res.Status = "failed"
	default:
		res.Status, res.Passed = "passed", true
	}
}

type limitedBuffer struct {
	mu  sync.Mutex
	buf bytes.Buffer
	cut bool
}

func (b *limitedBuffer) Write(p []byte) (int, error) {
	b.mu.Lock()
	defer b.mu.Unlock()
	if room := maxOutput - b.buf.Len(); room > 0 {
		if len(p) > room {
			b.buf.Write(p[:room])
			b.cut = true
		} else {
			b.buf.Write(p)
		}
	} else {
		b.cut = true
	}
	return len(p), nil
}

func (b *limitedBuffer) String() string {
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.cut {
		return b.buf.String() + "\n[output truncated]"
	}
	return b.buf.String()
}
