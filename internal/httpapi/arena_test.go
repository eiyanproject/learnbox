package httpapi

import (
	"encoding/json"
	"log/slog"
	"net/http"
	"net/http/httptest"
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

// arenaServer serves a track with one ordinary lesson and a two-step ladder:
// "one" is open, "two" needs "one" won.
func arenaServer(t *testing.T) (http.Handler, *progress.Store) {
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
	write("py/track.yaml", "title: Python\nsections:\n  - id: learn\n    title: Beginner\n  - id: arena\n    title: Arena\n    arena: true\n")
	write("py/learn/plain/lesson.md", "---\ntitle: plain\n---\nbody\n")
	write("py/learn/plain/tests/test_it.py", "def test_it(): pass\n")
	for i, slug := range []string{"one", "two"} {
		write("py/arena/"+slug+"/lesson.md", "---\ntitle: "+slug+"\norder: "+string(rune('1'+i))+"\nfiles: [a.py]\nchallenge:\n  minutes: 10\n  cooldown_minutes: 3\n  xp: 100\n---\nthe secret task\n")
		write("py/arena/"+slug+"/starter/a.py", "# start\n")
		write("py/arena/"+slug+"/tests/test_it.py", "def test_it(): pass\n")
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
		Log: slog.New(slog.DiscardHandler), WebDir: t.TempDir(), Lib: lib, Profiles: reg,
		Sandbox: sb, Workspace: ws, Terms: term.NewManager(sb, slog.New(slog.DiscardHandler)), Location: time.UTC,
	}).Handler()
	store, err := reg.Progress(profiles.DefaultID)
	if err != nil {
		t.Fatal(err)
	}
	return h, store
}

type challengeReply struct {
	Code      string             `json:"code"`
	Challenge game.ChallengeView `json:"challenge"`
	Outcome   string             `json:"outcome"`
	HTML      string             `json:"html"`
}

func reply(t *testing.T, w *httptest.ResponseRecorder) challengeReply {
	t.Helper()
	var out challengeReply
	if err := json.Unmarshal(w.Body.Bytes(), &out); err != nil {
		t.Fatalf("%s: %v", w.Body, err)
	}
	return out
}

const one, two = "/api/lessons/py/arena/one", "/api/lessons/py/arena/two"

func TestArenaListsTheLadderAndTracksLeaveItOut(t *testing.T) {
	h, _ := arenaServer(t)
	w := do(t, h, "GET", "/api/arena", "")
	var out struct {
		Ladders []game.Ladder `json:"ladders"`
	}
	if err := json.Unmarshal(w.Body.Bytes(), &out); err != nil || w.Code != http.StatusOK {
		t.Fatalf("arena: %d %s", w.Code, w.Body)
	}
	if len(out.Ladders) != 1 || len(out.Ladders[0].Challenges) != 2 {
		t.Fatalf("ladders: %+v", out.Ladders)
	}
	if c := out.Ladders[0].Challenges; c[0].State != game.Ready || c[1].State != game.Locked || c[0].MaxXP != 150 {
		t.Fatalf("states: %+v", c)
	}

	w = do(t, h, "GET", "/api/tracks", "")
	var tr struct {
		Tracks []struct {
			Total    int `json:"total"`
			Sections []struct {
				ID string `json:"id"`
			} `json:"sections"`
		} `json:"tracks"`
	}
	json.Unmarshal(w.Body.Bytes(), &tr)
	if len(tr.Tracks) != 1 || len(tr.Tracks[0].Sections) != 1 || tr.Tracks[0].Total != 1 {
		t.Fatalf("the arena should not be listed as lessons: %s", w.Body)
	}
}

func TestChallengeIsClosedUntilStarted(t *testing.T) {
	h, _ := arenaServer(t)
	for _, url := range []string{one, one + "/files/a.py", one + "/mtimes"} {
		w := do(t, h, "GET", url, "")
		if w.Code != http.StatusConflict || reply(t, w).Code != "challenge_not_started" {
			t.Errorf("GET %s before starting: %d %s", url, w.Code, w.Body)
		}
	}
	if w := do(t, h, "PUT", one+"/files/a.py", `{"content":"x"}`); w.Code != http.StatusConflict {
		t.Errorf("write before starting: %d", w.Code)
	}
	if w := do(t, h, "POST", one+"/hint", ""); w.Code != http.StatusBadRequest {
		t.Errorf("hint on a challenge: %d", w.Code)
	}
	// An ordinary lesson has no such gate, and no challenge routes.
	if w := do(t, h, "GET", "/api/lessons/py/learn/plain", ""); w.Code != http.StatusOK {
		t.Errorf("plain lesson: %d %s", w.Code, w.Body)
	}
	if w := do(t, h, "POST", "/api/lessons/py/learn/plain/challenge/start", ""); w.Code != http.StatusNotFound {
		t.Errorf("start on a plain lesson: %d", w.Code)
	}
}

func TestStartOpensTheChallengeAndRestoresTheStarter(t *testing.T) {
	h, store := arenaServer(t)
	w := do(t, h, "POST", one+"/challenge/start", "")
	got := reply(t, w)
	if w.Code != http.StatusOK || got.Challenge.State != game.Active || got.Challenge.Deadline.IsZero() {
		t.Fatalf("start: %d %s", w.Code, w.Body)
	}
	deadline := got.Challenge.Deadline

	if w := do(t, h, "GET", one, ""); w.Code != http.StatusOK || reply(t, w).HTML == "" {
		t.Fatalf("lesson during an attempt: %d %s", w.Code, w.Body)
	}
	if w := do(t, h, "PUT", one+"/files/a.py", `{"content":"mine"}`); w.Code != http.StatusOK {
		t.Fatalf("write during an attempt: %d %s", w.Code, w.Body)
	}
	// Starting again does not restart the clock or wipe the work.
	if again := reply(t, do(t, h, "POST", one+"/challenge/start", "")); !again.Challenge.Deadline.Equal(deadline) {
		t.Fatalf("a second start moved the deadline: %v -> %v", deadline, again.Challenge.Deadline)
	}
	var f workspace.File
	json.Unmarshal(do(t, h, "GET", one+"/files/a.py", "").Body.Bytes(), &f)
	if f.Content != "mine" {
		t.Fatalf("a second start wiped the work: %q", f.Content)
	}

	// Forfeit: a loss, a cooldown, and the door shuts again.
	lost := reply(t, do(t, h, "POST", one+"/challenge/forfeit", ""))
	if lost.Challenge.State != game.Cooldown || lost.Challenge.Losses != 1 {
		t.Fatalf("forfeit: %+v", lost.Challenge)
	}
	if w := do(t, h, "GET", one, ""); w.Code != http.StatusConflict {
		t.Fatalf("lesson after a loss: %d", w.Code)
	}
	if w := do(t, h, "POST", one+"/challenge/start", ""); w.Code != http.StatusConflict || reply(t, w).Code != "challenge_cooldown" {
		t.Fatalf("start in cooldown: %d %s", w.Code, w.Body)
	}

	// Once the cooldown is over a new attempt starts from the starter files.
	if _, err := store.UpdateChallenge("py/arena/one", func(c *progress.Challenge) { c.CooldownUntil = time.Now().Add(-time.Second) }); err != nil {
		t.Fatal(err)
	}
	if w := do(t, h, "POST", one+"/challenge/start", ""); w.Code != http.StatusOK {
		t.Fatalf("start after cooldown: %d %s", w.Code, w.Body)
	}
	json.Unmarshal(do(t, h, "GET", one+"/files/a.py", "").Body.Bytes(), &f)
	if f.Content != "# start\n" {
		t.Fatalf("a new attempt should begin from the starter: %q", f.Content)
	}
}

func TestRunningOutOfTimeIsALoss(t *testing.T) {
	h, store := arenaServer(t)
	if w := do(t, h, "POST", one+"/challenge/start", ""); w.Code != http.StatusOK {
		t.Fatalf("start: %d", w.Code)
	}
	past := time.Now().Add(-time.Minute)
	if _, err := store.UpdateChallenge("py/arena/one", func(c *progress.Challenge) {
		c.Started, c.Deadline = past.Add(-10*time.Minute), past
	}); err != nil {
		t.Fatal(err)
	}
	// A check sent after the deadline does not run: the attempt is over.
	w := do(t, h, "POST", one+"/check", "")
	if got := reply(t, w); w.Code != http.StatusOK || got.Outcome != "lost" {
		t.Fatalf("late check: %d %s", w.Code, w.Body)
	}
	c := store.Challenge("py/arena/one")
	if c.Active() || c.Losses != 1 || !c.CooldownUntil.Equal(past.Add(3*time.Minute)) {
		t.Fatalf("after time ran out: %+v", c)
	}
}

func TestLockedChallengeCannotBeStarted(t *testing.T) {
	h, store := arenaServer(t)
	w := do(t, h, "POST", two+"/challenge/start", "")
	if got := reply(t, w); w.Code != http.StatusForbidden || got.Code != "challenge_locked" || len(got.Challenge.Locks) != 1 {
		t.Fatalf("locked start: %d %s", w.Code, w.Body)
	}
	if _, err := store.UpdateChallenge("py/arena/one", func(c *progress.Challenge) { c.Wins, c.BestXP = 1, 120 }); err != nil {
		t.Fatal(err)
	}
	if w := do(t, h, "POST", two+"/challenge/start", ""); w.Code != http.StatusOK {
		t.Fatalf("start once the first is won: %d %s", w.Code, w.Body)
	}
	// A won challenge stays open without a clock, and its XP is counted.
	if w := do(t, h, "GET", one, ""); w.Code != http.StatusOK {
		t.Fatalf("a won challenge should open: %d", w.Code)
	}
	if sum := getSummary(t, h); sum.XP != 120 || !earned(sum, "arena-first") {
		t.Fatalf("summary after a win: %+v", sum.Standing)
	}
}
