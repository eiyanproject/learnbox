package runner

// Practice drills, Rust only. A lesson's src/drills.rs holds small functions,
// each under a "/// Drill N:" line, and its hidden tests/drills.rs their
// tests, named drill_NN_*. Built by cargo they would be one crate: a drill
// that does not compile would hide every other drill's result, and lib.rs
// would have to compile first. So rustc builds them alone instead. A drill
// that does not compile is cut out and the rest built again, and a single
// drill can be run by itself.

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"

	"github.com/eiyanproject/learnbox/internal/content"
)

var (
	drillMark    = regexp.MustCompile(`^\s*///\s*Drill (\d+):`)
	drillFn      = regexp.MustCompile(`^fn (drill_(\d+)_\w+)\(`)
	cargoEdition = regexp.MustCompile(`(?m)^edition\s*=\s*"(\d+)"`)
)

var ErrNoDrill = errors.New("no such drill")

func hasDrills(l *content.Lesson) bool { return len(l.Drills) > 0 }

// drillFile is a source file cut into drills. Lines before the first drill
// are shared by all of them; first is -1 when no drill is marked, and then
// every line is shared.
type drillFile struct {
	lines []string
	first int
	spans map[int][][2]int // drill → its line ranges, [start, end)
}

// splitDrills cuts lines into drills; starts reports the drill a line opens.
func splitDrills(src string, starts func(lines []string, i int) (int, bool)) *drillFile {
	f := &drillFile{lines: strings.Split(src, "\n"), first: -1, spans: map[int][][2]int{}}
	cur := -1
	for i := range f.lines {
		if n, ok := starts(f.lines, i); ok {
			if f.first < 0 {
				f.first = i
			}
			cur = n
			f.spans[n] = append(f.spans[n], [2]int{i, i})
		}
		if cur >= 0 {
			s := f.spans[cur]
			s[len(s)-1][1] = i + 1
		}
	}
	return f
}

// keep is the file with only the shared lines and the drills in keep. The
// rest become blank lines, so the compiler's line numbers still match the
// learner's file.
func (f *drillFile) keep(keep map[int]bool) string {
	if f.first < 0 {
		return strings.Join(f.lines, "\n")
	}
	out := make([]string, len(f.lines))
	copy(out, f.lines[:f.first])
	for n := range keep {
		for _, s := range f.spans[n] {
			copy(out[s[0]:s[1]], f.lines[s[0]:s[1]])
		}
	}
	return strings.Join(out, "\n")
}

// owner is the drill that line (1-based) belongs to, or -1 for a shared line.
func (f *drillFile) owner(line int) int {
	for n, ss := range f.spans {
		for _, s := range ss {
			if line-1 >= s[0] && line-1 < s[1] {
				return n
			}
		}
	}
	return -1
}

func markedDrill(lines []string, i int) (int, bool) {
	m := drillMark.FindStringSubmatch(lines[i])
	if m == nil {
		return 0, false
	}
	n, _ := strconv.Atoi(m[1])
	return n, true
}

// A test starts at its #[test] line; the fn on the next line says which drill.
func testedDrill(lines []string, i int) (int, bool) {
	if strings.TrimSpace(lines[i]) != "#[test]" || i+1 >= len(lines) {
		return 0, false
	}
	m := drillFn.FindStringSubmatch(lines[i+1])
	if m == nil {
		return 0, false
	}
	n, _ := strconv.Atoi(m[2])
	return n, true
}

type rustcDiag struct {
	Level    string `json:"level"`
	Rendered string `json:"rendered"`
	Spans    []struct {
		File string `json:"file_name"`
		Line int    `json:"line_start"`
	} `json:"spans"`
}

// CheckDrill builds and tests one drill of a lesson, from the files in srcRel
// (relative to the learner's home). It never counts as a check of the lesson.
func (r *Runner) CheckDrill(ctx context.Context, l *content.Lesson, srcRel string, n int) (*Result, error) {
	found := false
	for _, d := range l.Drills {
		found = found || d.N == n
	}
	if !found {
		return nil, fmt.Errorf("%w: %s has no drill %d", ErrNoDrill, l.ID(), n)
	}
	r.mu.Lock()
	defer r.mu.Unlock()
	checkRel, err := r.prepare(l, srcRel)
	if err != nil {
		return nil, err
	}
	return r.drills(ctx, l, checkRel, map[int]bool{n: true})
}

// drills builds and runs the drills in want (all of them when nil) from the
// copy of the workspace at checkRel. A drill that does not compile fails
// each of its tests with the compiler's message.
func (r *Runner) drills(ctx context.Context, l *content.Lesson, checkRel string, want map[int]bool) (*Result, error) {
	if want == nil {
		want = map[int]bool{}
		for _, d := range l.Drills {
			want[d.N] = true
		}
	}
	rawTests, err := os.ReadFile(filepath.Join(l.TestsDir(), "drills.rs"))
	if err != nil {
		return nil, err
	}
	tests := splitDrills(string(rawTests), testedDrill)
	names := map[int][]string{} // drill → its test fns
	for i := range tests.lines {
		if n, ok := testedDrill(tests.lines, i); ok {
			names[n] = append(names[n], drillFn.FindStringSubmatch(tests.lines[i+1])[1])
		}
	}

	res := &Result{}
	failed := map[int]string{}
	fail := func(n int, why string) {
		if failed[n] == "" {
			failed[n] = why
		}
	}
	src, err := r.ws.ReadFileRel(checkRel + "/src/drills.rs")
	if err != nil {
		for n := range want {
			fail(n, "src/drills.rs is missing. Reset the lesson to get it back.")
		}
		return r.drillResult(res, want, names, failed, nil, 1), nil
	}
	learner := splitDrills(string(src), markedDrill)

	edition := "2021"
	if toml, err := r.ws.ReadFileRel(checkRel + "/Cargo.toml"); err == nil {
		if m := cargoEdition.FindSubmatch(toml); m != nil {
			edition = string(m[1])
		}
	}
	workRel := checkRel + "/.drills"
	work := r.sb.Home + "/" + workRel
	if err := r.ws.MkdirAll(workRel + "/src"); err != nil {
		return nil, err
	}
	if err := r.ws.MkdirAll(workRel + "/tests"); err != nil {
		return nil, err
	}

	var out strings.Builder
	for {
		active := map[int]bool{}
		for n := range want {
			if failed[n] == "" {
				active[n] = true
			}
		}
		if len(active) == 0 {
			res.Output = out.String()
			return r.drillResult(res, want, names, failed, nil, 1), nil
		}
		if err := r.ws.WriteFileRel(workRel+"/src/drills.rs", []byte(learner.keep(active))); err != nil {
			return nil, err
		}
		if err := r.ws.WriteFileRel(workRel+"/tests/drills.rs", []byte(tests.keep(active))); err != nil {
			return nil, err
		}
		o, code, timedOut, dur, err := r.exec(ctx, work, nil, "rustc",
			"--edition", edition, "--test", "--error-format=json", "-A", "dead_code", "-A", "unused",
			"-o", "drills", "tests/drills.rs")
		if err != nil {
			return nil, err
		}
		res.DurationMS += dur.Milliseconds()
		if timedOut {
			res.Status, res.Output = "timeout", out.String()+o
			return res, nil
		}
		if code == 0 {
			break
		}
		blamed := false
		for _, line := range strings.Split(o, "\n") {
			var d rustcDiag
			if !strings.HasPrefix(line, "{") || json.Unmarshal([]byte(line), &d) != nil || d.Level != "error" || len(d.Spans) == 0 {
				continue
			}
			msg := strings.ReplaceAll(d.Rendered, "tests/../src/", "src/")
			out.WriteString(msg)
			// The earliest drill the error points into is the one to cut
			// out; an unclosed brace points at its opening line and at the
			// end of the file. An error only in shared lines fails them all.
			owner := -1
			for _, s := range d.Spans {
				n := -1
				if strings.HasSuffix(s.File, "src/drills.rs") && !strings.HasPrefix(s.File, "tests/drills") {
					n = learner.owner(s.Line)
				} else if s.File == "tests/drills.rs" {
					n = tests.owner(s.Line)
				}
				if n >= 0 && active[n] && (owner < 0 || n < owner) {
					owner = n
				}
			}
			if owner >= 0 {
				fail(owner, msg)
				blamed = true
			} else {
				for n := range active {
					fail(n, msg)
				}
				blamed = true
			}
		}
		if !blamed {
			// No error we could read: the raw output is all there is.
			out.WriteString(o)
			for n := range active {
				fail(n, o)
			}
		}
	}

	o, code, timedOut, dur, err := r.exec(ctx, work, nil, work+"/drills", "--include-ignored", "--test-threads=1", "--color=never")
	if err != nil {
		return nil, err
	}
	res.DurationMS += dur.Milliseconds()
	o = strings.ReplaceAll(o, "tests/../src/", "src/") // panics name the learner's file as they know it
	out.WriteString(o)
	res.Output = out.String()
	if timedOut {
		res.Status = "timeout"
		return res, nil
	}
	return r.drillResult(res, want, names, failed, parseRustTests(o), code), nil
}

// drillResult fills res with the tests that ran and, for each drill that did
// not compile, its tests failed with the compiler's message.
func (r *Runner) drillResult(res *Result, want map[int]bool, names map[int][]string, failed map[int]string, ran []TestResult, code int) *Result {
	res.Tests = ran
	for n, why := range failed {
		if !want[n] {
			continue
		}
		for _, name := range names[n] {
			res.Tests = append(res.Tests, TestResult{Name: prettyTestName(name), Passed: false, Message: "does not compile:\n" + trimCompileError(why)})
		}
	}
	sort.SliceStable(res.Tests, func(i, j int) bool { return res.Tests[i].Name < res.Tests[j].Name })
	if len(failed) > 0 {
		code = 1
	}
	finish(res, code)
	return res
}

// trimCompileError keeps a compiler message short enough for a result row.
func trimCompileError(s string) string {
	s = strings.TrimSpace(s)
	lines := strings.Split(s, "\n")
	if len(lines) > 14 {
		lines = append(lines[:14], "…")
	}
	return strings.Join(lines, "\n")
}

// prepareRust puts the hidden tests in the check directory's tests/.
func (r *Runner) prepareRust(l *content.Lesson, checkRel string) error {
	if err := r.ws.CopyIn(l.TestsDir(), checkRel+"/tests"); err != nil {
		return fmt.Errorf("copy tests: %w", err)
	}
	if hasDrills(l) {
		// rustc builds the drills; cargo must not build them as a target.
		return r.ws.RemoveAll(path.Join(checkRel, "tests", "drills.rs"))
	}
	return nil
}
