package runner

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"os/exec"
	"os/user"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/sandbox"
	"github.com/eiyanproject/learnbox/internal/workspace"
)

// These tests build real Rust lessons, so they need rustc and cargo and are
// skipped under -short.
func rustRunner(t *testing.T) (*Runner, *workspace.Manager, *content.Library) {
	t.Helper()
	if testing.Short() {
		t.Skip("builds Rust; skipped with -short")
	}
	if _, err := exec.LookPath("rustc"); err != nil {
		t.Skip("rustc not installed")
	}
	u, err := user.Current()
	if err != nil {
		t.Fatal(err)
	}
	sb, err := sandbox.New(u.Username, sandbox.Limits{}, slog.New(slog.DiscardHandler))
	if err != nil {
		t.Fatal(err)
	}
	sb.Home = t.TempDir()
	ws, err := workspace.New(sb)
	if err != nil {
		t.Fatal(err)
	}
	lib, err := content.Load("../../content")
	if err != nil {
		t.Fatal(err)
	}
	return New(sb, ws, 2*time.Minute), ws, lib
}

// place copies one of a lesson's trees to rel, then lets edit change files.
func place(t *testing.T, ws *workspace.Manager, from, rel string, edit map[string]func(string) string) {
	t.Helper()
	// A solution holds only the files it changes: the starter goes first.
	for _, dir := range []string{filepath.Join(filepath.Dir(from), "starter"), from} {
		if err := ws.CopyIn(dir, rel); err != nil {
			t.Fatal(err)
		}
	}
	for name, f := range edit {
		raw, err := ws.ReadFileRel(rel + "/" + name)
		if err != nil {
			t.Fatal(err)
		}
		if err := ws.WriteFileRel(rel+"/"+name, []byte(f(string(raw)))); err != nil {
			t.Fatal(err)
		}
	}
}

func drillTests(res *Result) map[string]TestResult {
	out := map[string]TestResult{}
	for _, tr := range res.Tests {
		if strings.HasPrefix(tr.Name, "drill ") {
			out[tr.Name] = tr
		}
	}
	return out
}

func TestEveryRustDrillPassesOnItsOwn(t *testing.T) {
	r, ws, lib := rustRunner(t)
	ctx := context.Background()
	dirs, _ := filepath.Glob("../../content/rust/learn/*")
	for _, dir := range dirs {
		l := lib.Lesson("rust/learn/" + filepath.Base(dir))
		if l == nil || !hasDrills(l) {
			continue
		}
		rel := "sol/" + l.Slug
		place(t, ws, l.SolutionDir(), rel, nil)
		full, err := r.CheckDir(ctx, l, rel)
		if err != nil || !full.Passed {
			t.Errorf("%s solution: %v %+v", l.ID(), err, full)
		}
		start := "start/" + l.Slug
		if err := ws.CopyIn(l.StarterDir(), start); err != nil {
			t.Fatal(err)
		}
		if res, err := r.CheckDir(ctx, l, start); err != nil || res.Passed || len(drillTests(res)) != len(l.Drills) {
			t.Errorf("%s starter: want every drill run and the lesson failed: %v %+v", l.ID(), err, res)
		}
		for _, d := range l.Drills {
			res, err := r.CheckDrill(ctx, l, rel, d.N)
			if err != nil {
				t.Fatalf("%s drill %d: %v", l.ID(), d.N, err)
			}
			if !res.Passed || len(res.Tests) == 0 {
				t.Errorf("%s drill %d: %s\n%s", l.ID(), d.N, res.Status, res.Output)
			}
			for _, tr := range res.Tests {
				if !strings.HasPrefix(tr.Name, fmt.Sprintf("drill %02d ", d.N)) {
					t.Errorf("%s drill %d ran %q too", l.ID(), d.N, tr.Name)
				}
			}
		}
	}
}

func TestABrokenDrillFailsAloneAndTheRestStillRun(t *testing.T) {
	r, ws, lib := rustRunner(t)
	l := lib.Lesson("rust/learn/01-hello-cargo")
	for name, broken := range map[string]string{
		"type error":     `"not a number" + 1`,
		"unclosed brace": `{ {`,
	} {
		t.Run(name, func(t *testing.T) {
			rel := "broken/" + strings.ReplaceAll(name, " ", "-")
			place(t, ws, l.SolutionDir(), rel, map[string]func(string) string{
				"src/drills.rs": func(s string) string {
					// Drill 3's body: the first `{` after its marker.
					i := strings.Index(s, "/// Drill 3:")
					j := i + strings.Index(s[i:], "{\n") + 2
					return s[:j] + "    " + broken + "\n" + s[j:]
				},
			})
			res, err := r.CheckDir(context.Background(), l, rel)
			if err != nil {
				t.Fatal(err)
			}
			drills := drillTests(res)
			if len(drills) != len(l.Drills) {
				t.Fatalf("got %d drill results, want %d:\n%s", len(drills), len(l.Drills), res.Output)
			}
			for name, tr := range drills {
				three := strings.HasPrefix(name, "drill 03 ")
				if tr.Passed == three {
					t.Errorf("%s: passed=%v\n%s", name, tr.Passed, tr.Message)
				}
				if three && !strings.Contains(tr.Message, "does not compile") {
					t.Errorf("%s: message %q", name, tr.Message)
				}
			}
			if res.Passed {
				t.Error("lesson passed with a broken drill")
			}
			// The task's own tests still ran and passed.
			task := 0
			for _, tr := range res.Tests {
				if !strings.HasPrefix(tr.Name, "drill ") {
					task++
					if !tr.Passed {
						t.Errorf("task test %s failed", tr.Name)
					}
				}
			}
			if task == 0 {
				t.Errorf("no task tests ran:\n%s", res.Output)
			}
		})
	}
}

func TestDrillsRunWhileLibDoesNotCompile(t *testing.T) {
	r, ws, lib := rustRunner(t)
	l := lib.Lesson("rust/learn/04-ownership")
	rel := "nolib"
	place(t, ws, l.StarterDir(), rel, nil) // the starter's lib.rs is broken on purpose
	sol, err := os.ReadFile(filepath.Join(l.SolutionDir(), "src/drills.rs"))
	if err != nil {
		t.Fatal(err)
	}
	if err := ws.WriteFileRel(rel+"/src/drills.rs", sol); err != nil {
		t.Fatal(err)
	}
	res, err := r.CheckDir(context.Background(), l, rel)
	if err != nil {
		t.Fatal(err)
	}
	if res.Status != "error" {
		t.Errorf("status %s, want error", res.Status)
	}
	drills := drillTests(res)
	if len(drills) != len(l.Drills) {
		t.Fatalf("got %d drill results, want %d:\n%s", len(drills), len(l.Drills), res.Output)
	}
	for name, tr := range drills {
		if !tr.Passed {
			t.Errorf("%s failed: %s", name, tr.Message)
		}
	}
	one, err := r.CheckDrill(context.Background(), l, rel, 1)
	if err != nil || !one.Passed {
		t.Errorf("drill 1 alone: %v %+v", err, one)
	}
}
