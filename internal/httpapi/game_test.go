package httpapi

import (
	"encoding/json"
	"log/slog"
	"net/http"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/game"
	"github.com/eiyanproject/learnbox/internal/profiles"
	"github.com/eiyanproject/learnbox/internal/progress"
	"github.com/eiyanproject/learnbox/internal/sandbox"
	"github.com/eiyanproject/learnbox/internal/term"
	"github.com/eiyanproject/learnbox/internal/workspace"
)

// gameServer serves one track, "py", whose 50 XP section holds two lessons
// with two hints each.
func gameServer(t *testing.T) (http.Handler, *progress.Store) {
	t.Helper()
	root := t.TempDir()
	write := func(rel, body string) {
		p := filepath.Join(root, rel)
		if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(p, []byte(body), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	write("py/track.yaml", "title: Python\nsections:\n  - id: learn\n    title: Beginner\n    xp: 50\n")
	for _, slug := range []string{"one", "two"} {
		write("py/learn/"+slug+"/lesson.md", "---\ntitle: "+slug+"\nhints: [a, b]\n---\nbody\n")
		write("py/learn/"+slug+"/tests/test_it.py", "def test_it(): pass\n")
	}
	lib, err := content.Load(root)
	if err != nil {
		t.Fatal(err)
	}

	reg, err := profiles.Open(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	sb := &sandbox.Sandbox{Home: t.TempDir()}
	ws, err := workspace.New(sb)
	if err != nil {
		t.Fatal(err)
	}
	h := New(Deps{
		Log:       slog.New(slog.DiscardHandler),
		WebDir:    t.TempDir(),
		Lib:       lib,
		Profiles:  reg,
		Workspace: ws,
		Terms:     term.NewManager(sb, slog.New(slog.DiscardHandler)),
		Location:  time.UTC,
	}).Handler()
	store, err := reg.Progress(profiles.DefaultID)
	if err != nil {
		t.Fatal(err)
	}
	return h, store
}

func getSummary(t *testing.T, h http.Handler) game.Summary {
	t.Helper()
	w := do(t, h, "GET", "/api/summary", "")
	if w.Code != http.StatusOK {
		t.Fatalf("summary: %d %s", w.Code, w.Body)
	}
	var sum game.Summary
	if err := json.Unmarshal(w.Body.Bytes(), &sum); err != nil {
		t.Fatal(err)
	}
	return sum
}

func earned(sum game.Summary, id string) bool {
	for _, b := range sum.Badges {
		if b.ID == id {
			return b.Earned
		}
	}
	return false
}

func TestSummaryStartsEmpty(t *testing.T) {
	h, _ := gameServer(t)
	sum := getSummary(t, h)
	if sum.XP != 0 || sum.Level != 1 || sum.NextLevel != 100 || len(sum.Badges) == 0 {
		t.Fatalf("empty summary: %+v", sum.Standing)
	}
	if earned(sum, "first-pass") {
		t.Fatal("nothing passed, nothing earned")
	}
}

// A lesson passed before any of this existed has no pass_attempts and no
// badges on record. It still counts, and the summary writes the badges down.
func TestSummaryCountsOldPassesAndRecordsTheirBadges(t *testing.T) {
	h, store := gameServer(t)
	if _, err := store.Update("py/learn/one", func(e *progress.Entry) {
		e.Status, e.Attempts, e.HintsRevealed = progress.Passed, 3, 1
		e.PassedAt = time.Date(2026, 9, 20, 12, 0, 0, 0, time.UTC)
	}); err != nil {
		t.Fatal(err)
	}
	sum := getSummary(t, h)
	if sum.XP != 45 || sum.Passed != 1 {
		t.Fatalf("xp %d passed %d, want 45 and 1", sum.XP, sum.Passed)
	}
	if !earned(sum, "first-pass") {
		t.Fatal("first-pass should be earned")
	}
	if _, ok := store.Snapshot().Badges["first-pass"]; !ok {
		t.Fatal("the badge was not written to the store")
	}
}

func TestHintsCostUntilTheLessonIsPassed(t *testing.T) {
	h, store := gameServer(t)
	hint := func() int {
		t.Helper()
		w := do(t, h, "POST", "/api/lessons/py/learn/one/hint", "")
		if w.Code != http.StatusOK {
			t.Fatalf("hint: %d %s", w.Code, w.Body)
		}
		var out struct {
			XP int `json:"xp"`
		}
		json.Unmarshal(w.Body.Bytes(), &out)
		return out.XP
	}
	if xp := hint(); xp != 45 {
		t.Fatalf("after one hint the lesson should pay 45, got %d", xp)
	}
	if _, err := store.Update("py/learn/one", func(e *progress.Entry) { e.Status = progress.Passed }); err != nil {
		t.Fatal(err)
	}
	if xp := hint(); xp != 45 {
		t.Fatalf("a hint read after passing is free, got %d", xp)
	}
	if e := store.Get("py/learn/one"); e.HintsRevealed != 2 || e.FreeHints != 1 {
		t.Fatalf("entry: %+v", e)
	}
	if sum := getSummary(t, h); sum.XP != 45 {
		t.Fatalf("xp %d, want 45", sum.XP)
	}
}

func TestSummaryNeedsAProfile(t *testing.T) {
	h, _ := gameServer(t)
	if w := do(t, h, "POST", "/api/profiles", `{"name":"Ana"}`); w.Code != http.StatusCreated {
		t.Fatalf("create: %d", w.Code)
	}
	if w := do(t, h, "GET", "/api/summary", ""); w.Code != http.StatusConflict {
		t.Fatalf("got %d, want 409", w.Code)
	}
}
