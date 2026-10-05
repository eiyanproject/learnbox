package game

import (
	"slices"
	"strings"
	"testing"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/progress"
)

// arenaLibrary is the test library with a three-step Python ladder: an open
// round, a round needing 100 XP in the track, and a boss needing a badge.
func arenaLibrary() *content.Library {
	lib := library()
	ladder := lessons("py", "arena", 3)
	ladder[0].Title, ladder[1].Title, ladder[2].Title = "Round 1", "Round 2", "Boss"
	ladder[0].Challenge = &content.Challenge{Minutes: 10, CooldownMinutes: 3, XP: 100}
	ladder[1].Challenge = &content.Challenge{Minutes: 10, CooldownMinutes: 3, XP: 200, Requires: content.Requires{XP: 100}}
	ladder[2].Challenge = &content.Challenge{Boss: true, Minutes: 20, CooldownMinutes: 5, XP: 500, Requires: content.Requires{Badges: []string{"beginner-1"}}}
	lib.Tracks[0].Sections = append(lib.Tracks[0].Sections, content.Section{ID: "arena", Arena: true, Lessons: ladder})
	return lib
}

func states(lib *content.Library, snap progress.Snapshot, now time.Time) []string {
	var out []string
	for _, c := range Arena(lib, snap, time.UTC, now)[0].Challenges {
		out = append(out, c.State)
	}
	return out
}

func TestChallengeXPRewardsSpeed(t *testing.T) {
	limit := 10 * time.Minute
	for used, want := range map[time.Duration]int{
		0:                150, // the whole bonus
		5 * time.Minute:  125,
		10 * time.Minute: 100,
		12 * time.Minute: 100, // never below the base
	} {
		if got := ChallengeXP(100, limit, used); got != want {
			t.Errorf("used %v: got %d, want %d", used, got, want)
		}
	}
}

func TestLadderUnlocksInOrderAndByRequirement(t *testing.T) {
	lib := arenaLibrary()
	snap := snapshot(nil)
	if got := states(lib, snap, noon); !slices.Equal(got, []string{Ready, Locked, Locked}) {
		t.Fatalf("fresh ladder: %v", got)
	}
	r2 := Arena(lib, snap, time.UTC, noon)[0].Challenges[1]
	if len(r2.Locks) != 2 || !strings.Contains(r2.Locks[0], "Round 1") || !strings.Contains(r2.Locks[1], "100 more XP") {
		t.Errorf("round 2 locks: %q", r2.Locks)
	}

	// Winning round 1 pays into the track, which is what round 2 asks for.
	snap.Challenges["py/arena/l01"] = progress.Challenge{Wins: 1, BestXP: 120, FirstWonAt: noon}
	if got := states(lib, snap, noon); !slices.Equal(got, []string{Won, Ready, Locked}) {
		t.Fatalf("after round 1: %v", got)
	}

	snap.Challenges["py/arena/l02"] = progress.Challenge{Wins: 1, BestXP: 200, FirstWonAt: noon}
	boss := Arena(lib, snap, time.UTC, noon)[0].Challenges[2]
	if boss.State != Locked || len(boss.Locks) != 1 || !strings.Contains(boss.Locks[0], "Not a Beginner Anymore!") {
		t.Fatalf("boss should wait for the badge: %+v", boss)
	}
	snap.Badges["beginner-1"] = noon
	if got := states(lib, snap, noon); got[2] != Ready {
		t.Fatalf("boss with the badge: %v", got)
	}
}

func TestAttemptLifecycle(t *testing.T) {
	lib := arenaLibrary()
	ch := lib.Tracks[0].Sections[3].Lessons[0].Challenge
	var c progress.Challenge
	snapWith := func() progress.Snapshot {
		s := snapshot(nil)
		s.Challenges["py/arena/l01"] = c
		return s
	}

	StartChallenge(&c, ch, noon)
	if got := states(lib, snapWith(), noon.Add(9*time.Minute))[0]; got != Active {
		t.Fatalf("mid-attempt: %s", got)
	}
	if Expired(c, noon.Add(9*time.Minute)) || !Expired(c, noon.Add(10*time.Minute)) {
		t.Fatal("the attempt expires at its deadline, not before")
	}

	// Time runs out: a loss, then a cooldown, then ready again.
	lost := noon.Add(10 * time.Minute)
	LoseChallenge(&c, ch, lost)
	if c.Active() || c.Losses != 1 {
		t.Fatalf("after a loss: %+v", c)
	}
	if got := states(lib, snapWith(), lost.Add(2*time.Minute))[0]; got != Cooldown {
		t.Fatalf("in cooldown: %s", got)
	}
	if got := states(lib, snapWith(), lost.Add(3*time.Minute))[0]; got != Ready {
		t.Fatalf("after cooldown: %s", got)
	}

	// Second attempt, won at half time.
	again := lost.Add(5 * time.Minute)
	StartChallenge(&c, ch, again)
	xp := WinChallenge(&c, ch, again.Add(5*time.Minute))
	if xp != 125 || c.Wins != 1 || c.LossesBeforeWin != 1 || c.BestSeconds != 300 || c.BestFraction != 50 || c.BestXP != 125 || c.Active() {
		t.Fatalf("after a win: xp %d, %+v", xp, c)
	}

	// A slower replay does not lower the best; a faster one raises it.
	StartChallenge(&c, ch, again)
	WinChallenge(&c, ch, again.Add(9*time.Minute))
	if c.BestXP != 125 || c.BestSeconds != 300 || c.Wins != 2 || c.LossesBeforeWin != 1 {
		t.Fatalf("after a slower win: %+v", c)
	}
	StartChallenge(&c, ch, again)
	WinChallenge(&c, ch, again.Add(time.Minute))
	if c.BestXP != 145 || c.BestSeconds != 60 || c.BestFraction != 10 {
		t.Fatalf("after a faster win: %+v", c)
	}
	if got := states(lib, snapWith(), again)[0]; got != Won {
		t.Fatalf("won: %s", got)
	}
}

func TestArenaBadges(t *testing.T) {
	lib := arenaLibrary()
	snap := snapshot(nil)
	snap.Challenges["py/arena/l01"] = progress.Challenge{Wins: 1, BestXP: 140, BestFraction: 20, LossesBeforeWin: 3, FirstWonAt: noon}
	got := Qualified(lib, snap, time.UTC)
	for _, id := range []string{"arena-first", "arena-fast", "arena-comeback"} {
		if !slices.Contains(got, id) {
			t.Errorf("missing %s", id)
		}
	}
	if slices.Contains(got, "boss-1") || slices.Contains(got, "boss-all") {
		t.Error("no boss beaten yet")
	}
	snap.Challenges["py/arena/l03"] = progress.Challenge{Wins: 1, BestXP: 500, BestFraction: 90, FirstWonAt: noon}
	got = Qualified(lib, snap, time.UTC)
	for _, id := range []string{"boss-1", "boss-all", "boss-flawless"} {
		if !slices.Contains(got, id) {
			t.Errorf("missing %s", id)
		}
	}
	// With no boss anywhere, "every boss" is not earned by default.
	if slices.Contains(Qualified(library(), snapshot(nil), time.UTC), "boss-all") {
		t.Error("boss-all earned with no bosses")
	}
}

func TestValidateCatchesUnknownBadges(t *testing.T) {
	lib := arenaLibrary()
	if err := Validate(lib); err != nil {
		t.Fatal(err)
	}
	lib.Tracks[0].Sections[3].Lessons[0].Challenge.Requires.Badges = []string{"no-such-badge"}
	if err := Validate(lib); err == nil {
		t.Fatal("an unknown badge should be refused")
	}
}
