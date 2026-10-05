package game

import (
	"fmt"
	"slices"
	"testing"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/progress"
)

// lessons builds n testable lessons, each with two hints.
func lessons(lang, section string, n int) []*content.Lesson {
	var out []*content.Lesson
	for i := range n {
		out = append(out, &content.Lesson{
			Lang: lang, Section: section, Slug: fmt.Sprintf("l%02d", i+1),
			Title: "L", HasTest: true, Hints: []string{"a", "b"},
		})
	}
	return out
}

// library is two tracks: py (a 50 XP beginner section of 4, a default-XP
// section of 2, three rated practice exercises) and rs (a 75 XP section of 3).
func library() *content.Library {
	practice := lessons("py", "practice", 3)
	for i, l := range practice {
		l.Difficulty = []int{1, 4, 12}[i]
		l.Hints = nil
	}
	return &content.Library{Tracks: []*content.Track{
		{Lang: "py", Title: "Python", Badge: "Pythonista", Sections: []content.Section{
			{ID: "learn", XP: 50, Beginner: true, Lessons: lessons("py", "learn", 4)},
			{ID: "pro", Lessons: lessons("py", "pro", 2)},
			{ID: "practice", Lessons: practice},
		}},
		{Lang: "rs", Title: "Rust", Sections: []content.Section{
			{ID: "learn", XP: 75, Lessons: lessons("rs", "learn", 3)},
		}},
	}}
}

var noon = time.Date(2026, 3, 4, 12, 0, 0, 0, time.UTC) // a Wednesday

func pass(at time.Time) progress.Entry {
	return progress.Entry{Status: progress.Passed, Attempts: 2, PassAttempts: 2, PassedAt: at, FirstOpened: at.Add(-time.Hour)}
}

func snapshot(lessons map[string]progress.Entry) progress.Snapshot {
	return progress.Snapshot{Lessons: lessons, Challenges: map[string]progress.Challenge{}, Badges: map[string]time.Time{}}
}

func qualifies(t *testing.T, snap progress.Snapshot, id string) bool {
	t.Helper()
	return slices.Contains(Qualified(library(), snap, time.UTC), id)
}

func TestLessonXP(t *testing.T) {
	sec := &content.Section{XP: 75}
	for _, c := range []struct {
		sec        *content.Section
		difficulty int
		want       int
	}{
		{sec, 0, 75},
		{&content.Section{}, 0, DefaultLessonXP},
		{sec, 4, 40},                  // a rating wins over the section
		{&content.Section{}, 12, 100}, // and is capped at 10 points
	} {
		if got := LessonXP(c.sec, &content.Lesson{Difficulty: c.difficulty}); got != c.want {
			t.Errorf("xp %d difficulty %d: got %d, want %d", c.sec.XP, c.difficulty, got, c.want)
		}
	}
}

func TestHintsCostTenPercentDownToHalf(t *testing.T) {
	for hints, want := range map[int]int{0: 100, 1: 90, 3: 70, 5: 50, 6: 50, 40: 50} {
		if got := AfterHints(100, hints); got != want {
			t.Errorf("%d hints: got %d, want %d", hints, got, want)
		}
	}
	if got := AfterHints(75, 1); got != 67 {
		t.Errorf("75 XP less one hint: got %d, want 67", got)
	}
}

func TestHintsAfterThePassAreFree(t *testing.T) {
	e := pass(noon)
	e.HintsRevealed, e.FreeHints = 2, 1
	if got := PaidHints(e); got != 1 {
		t.Fatalf("paid hints: got %d, want 1", got)
	}
	sum := Summarize(library(), snapshot(map[string]progress.Entry{"py/pro/l01": e}), time.UTC)
	if sum.XP != 90 {
		t.Fatalf("xp: got %d, want 90", sum.XP)
	}
}

func TestLevels(t *testing.T) {
	for xp, want := range map[int]int{0: 1, 99: 1, 100: 2, 299: 2, 300: 3, 600: 4, 4499: 9, 4500: 10} {
		if got := LevelFor(xp); got != want {
			t.Errorf("%d XP: level %d, want %d", xp, got, want)
		}
	}
	s := standing(350)
	if s.Level != 3 || s.LevelFloor != 300 || s.NextLevel != 600 || s.Title != "Newcomer" {
		t.Errorf("standing(350) = %+v", s)
	}
	if TitleFor(5) != "Tinkerer" || TitleFor(99) != "Legend" {
		t.Errorf("titles: %q %q", TitleFor(5), TitleFor(99))
	}
}

func TestSummaryCountsOnlyPassedLessonsThatExist(t *testing.T) {
	started := progress.Entry{Status: progress.Started, HintsRevealed: 2}
	sum := Summarize(library(), snapshot(map[string]progress.Entry{
		"py/learn/l01":    pass(noon),
		"py/learn/l02":    started,
		"py/practice/l02": pass(noon),
		"rs/learn/l01":    pass(noon),
		"py/gone/l01":     pass(noon), // a lesson since removed
	}), time.UTC)

	if sum.XP != 50+40+75 || sum.Passed != 3 {
		t.Fatalf("xp %d passed %d, want 165 and 3", sum.XP, sum.Passed)
	}
	py, rs := sum.Tracks[0], sum.Tracks[1]
	if py.XP != 90 || py.Possible != 4*50+2*100+10+40+100 {
		t.Errorf("python: %+v", py)
	}
	if rs.XP != 75 || rs.Possible != 225 {
		t.Errorf("rust: %+v", rs)
	}
}

func TestArenaWinsPayWhatWasRecorded(t *testing.T) {
	lib := library()
	arena := lessons("py", "arena", 2)
	lib.Tracks[0].Sections = append(lib.Tracks[0].Sections, content.Section{ID: "arena", Arena: true, Lessons: arena})
	snap := snapshot(map[string]progress.Entry{"py/arena/l01": pass(noon)})
	snap.Challenges["py/arena/l01"] = progress.Challenge{Wins: 1, BestXP: 180, FirstWonAt: noon}
	snap.Challenges["py/arena/l02"] = progress.Challenge{Losses: 2}

	sum := Summarize(lib, snap, time.UTC)
	if sum.XP != 180 || sum.Passed != 0 {
		t.Fatalf("xp %d passed %d, want 180 and 0", sum.XP, sum.Passed)
	}
	if sum.Tracks[0].Possible != 550 {
		t.Errorf("arena lessons should not count as lesson XP: possible %d", sum.Tracks[0].Possible)
	}
}

func TestBadgesShowEarnedOnlyOnceRecorded(t *testing.T) {
	snap := snapshot(map[string]progress.Entry{"py/learn/l01": pass(noon)})
	find := func(sum Summary, id string) Badge {
		for _, b := range sum.Badges {
			if b.ID == id {
				return b
			}
		}
		t.Fatalf("no badge %s", id)
		return Badge{}
	}

	if !qualifies(t, snap, "first-pass") {
		t.Fatal("one pass should qualify for first-pass")
	}
	if b := find(Summarize(library(), snap, time.UTC), "first-pass"); b.Earned || b.Have != 1 || b.Want != 1 {
		t.Errorf("unrecorded badge: %+v", b)
	}
	snap.Badges["first-pass"] = noon
	if b := find(Summarize(library(), snap, time.UTC), "first-pass"); !b.Earned || !b.EarnedAt.Equal(noon) {
		t.Errorf("recorded badge: %+v", b)
	}

	// Recorded badges stay even when nothing qualifies any more.
	kept := snapshot(nil)
	kept.Badges["lessons-10"] = noon
	if b := find(Summarize(library(), kept, time.UTC), "lessons-10"); !b.Earned {
		t.Errorf("a recorded badge was lost: %+v", b)
	}
	if b := find(Summarize(library(), kept, time.UTC), "lessons-50"); b.Have != 0 || b.Want != 50 {
		t.Errorf("progress: %+v", b)
	}
}

func TestSecretBadgesGiveNothingAway(t *testing.T) {
	e := pass(noon)
	e.PassAttempts = 13
	snap := snapshot(map[string]progress.Entry{"py/learn/l01": e})
	for _, b := range Summarize(library(), snap, time.UTC).Badges {
		if b.Family == Secret && (b.Name != "???" || b.Have != 0 || b.Want != 0) {
			t.Errorf("secret badge leaks before it is earned: %+v", b)
		}
	}
	if !qualifies(t, snap, "lucky-13") {
		t.Fatal("thirteenth attempt should qualify")
	}
	snap.Badges["lucky-13"] = noon
	for _, b := range Summarize(library(), snap, time.UTC).Badges {
		if b.ID == "lucky-13" && b.Name != "Lucky Thirteen" {
			t.Errorf("earned secret badge: %+v", b)
		}
	}
}

func TestCompletionBadges(t *testing.T) {
	all := map[string]progress.Entry{}
	for i := 1; i <= 4; i++ {
		all[fmt.Sprintf("py/learn/l%02d", i)] = pass(noon)
	}
	snap := snapshot(all)
	if !qualifies(t, snap, "beginner-1") || !qualifies(t, snap, "no-hints") {
		t.Error("a finished Beginner section with no hints should earn both badges")
	}
	if qualifies(t, snap, "track-py") {
		t.Error("the track badge needs every guided lesson")
	}

	// One paid hint spoils the no-hint badge; a free one does not.
	e := all["py/learn/l03"]
	e.HintsRevealed, e.FreeHints = 1, 1
	all["py/learn/l03"] = e
	if !qualifies(t, snapshot(all), "no-hints") {
		t.Error("a hint read after the pass should not count")
	}
	e.FreeHints = 0
	all["py/learn/l03"] = e
	if qualifies(t, snapshot(all), "no-hints") {
		t.Error("a paid hint should spoil the badge")
	}

	// Practice exercises are not part of the track badge.
	all["py/pro/l01"], all["py/pro/l02"] = pass(noon), pass(noon)
	if !qualifies(t, snapshot(all), "track-py") {
		t.Error("every guided lesson passed should earn the track badge")
	}
	if qualifies(t, snapshot(all), "tracks-all") {
		t.Error("one of two tracks is not every track")
	}
	all["rs/learn/l01"] = pass(noon)
	if !qualifies(t, snapshot(all), "tracks-all") {
		t.Error("a pass in both tracks should earn tracks-all")
	}
}

func TestTrackBadgeNames(t *testing.T) {
	names := map[string]string{}
	for _, b := range Summarize(library(), snapshot(nil), time.UTC).Badges {
		names[b.ID] = b.Name
	}
	if names["track-py"] != "Pythonista" || names["track-rs"] != "Finished Rust" {
		t.Errorf("track badges: %q, %q", names["track-py"], names["track-rs"])
	}
}

func TestStyleBadges(t *testing.T) {
	e := pass(noon)
	e.PassAttempts, e.Attempts = 1, 6 // checked again after passing
	if got := compute(library(), snapshot(map[string]progress.Entry{"py/learn/l01": e}), time.UTC).firstTry; got != 1 {
		t.Errorf("first-try passes: got %d, want 1", got)
	}
	// A pass from before attempts were recorded falls back to the total.
	old := progress.Entry{Status: progress.Passed, Attempts: 1, PassedAt: noon}
	if got := compute(library(), snapshot(map[string]progress.Entry{"py/learn/l01": old}), time.UTC).firstTry; got != 1 {
		t.Errorf("legacy first-try passes: got %d, want 1", got)
	}

	e.PassAttempts = 11
	if !qualifies(t, snapshot(map[string]progress.Entry{"py/learn/l01": e}), "persistent") {
		t.Error("eleven attempts should earn persistent")
	}
	e.HintsRevealed = 2
	if !qualifies(t, snapshot(map[string]progress.Entry{"py/learn/l01": e}), "all-hints") {
		t.Error("every hint read should earn all-hints")
	}
}

func TestCalendarBadges(t *testing.T) {
	day := func(d int, hour int) time.Time { return time.Date(2026, 3, d, hour, 0, 0, 0, time.UTC) }
	run := func(times ...time.Time) progress.Snapshot {
		m := map[string]progress.Entry{}
		ids := []string{"py/learn/l01", "py/learn/l02", "py/learn/l03", "py/learn/l04", "py/pro/l01", "py/pro/l02", "rs/learn/l01"}
		for i, at := range times {
			m[ids[i]] = pass(at)
		}
		return snapshot(m)
	}

	// 2nd-4th in a row, a gap, then the 6th.
	st := compute(library(), run(day(2, 12), day(3, 12), day(4, 12), day(6, 12)), time.UTC)
	if st.streak != 3 || st.bestDay != 1 {
		t.Errorf("streak %d bestDay %d, want 3 and 1", st.streak, st.bestDay)
	}

	// 7 March 2026 is a Saturday.
	if !qualifies(t, run(day(7, 12), day(8, 12)), "weekend") {
		t.Error("Saturday and Sunday should earn weekend")
	}
	if qualifies(t, run(day(8, 12), day(9, 12)), "weekend") {
		t.Error("Sunday and Monday are not a weekend")
	}
	if qualifies(t, run(day(7, 12), day(15, 12)), "weekend") {
		t.Error("Saturday and next week's Sunday are not one weekend")
	}

	if !qualifies(t, run(day(2, 3)), "night-owl") || qualifies(t, run(day(2, 3)), "early-bird") {
		t.Error("03:00 is a night owl, not an early bird")
	}
	if !qualifies(t, run(day(2, 6)), "early-bird") {
		t.Error("06:00 is an early bird")
	}
	if !qualifies(t, run(day(2, 9), day(2, 10), day(2, 11), day(2, 12), day(2, 13)), "day-5") {
		t.Error("five passes in a day should earn day-5")
	}
}

func TestTheDayIsTheLearnersNotUTC(t *testing.T) {
	tokyo := time.FixedZone("JST", 9*3600)
	// 18:30 UTC on Friday is 03:30 on Saturday in Tokyo.
	at := time.Date(2026, 3, 6, 18, 30, 0, 0, time.UTC)
	snap := snapshot(map[string]progress.Entry{"py/learn/l01": pass(at)})
	if slices.Contains(Qualified(library(), snap, time.UTC), "night-owl") {
		t.Error("18:30 is not night in UTC")
	}
	if !slices.Contains(Qualified(library(), snap, tokyo), "night-owl") {
		t.Error("03:30 in Tokyo should be a night owl")
	}
	// New Year arrives in Tokyo while it is still 31 December in UTC.
	eve := time.Date(2026, 12, 31, 16, 0, 0, 0, time.UTC)
	snap = snapshot(map[string]progress.Entry{"py/learn/l01": pass(eve)})
	if !slices.Contains(Qualified(library(), snap, tokyo), "new-year") {
		t.Error("01:00 on 1 January in Tokyo should earn new-year")
	}
}

func TestSpeedrun(t *testing.T) {
	e := pass(noon)
	e.FirstOpened = noon.Add(-90 * time.Second)
	if !qualifies(t, snapshot(map[string]progress.Entry{"py/learn/l01": e}), "speedrun") {
		t.Error("ninety seconds should earn speedrun")
	}
	e.FirstOpened = time.Time{} // unknown: no badge
	if qualifies(t, snapshot(map[string]progress.Entry{"py/learn/l01": e}), "speedrun") {
		t.Error("an unknown opening time should not earn speedrun")
	}
}

func TestDiff(t *testing.T) {
	lib := library()
	before := Summarize(lib, snapshot(map[string]progress.Entry{"py/learn/l01": pass(noon)}), time.UTC)
	snap := snapshot(map[string]progress.Entry{"py/learn/l01": pass(noon), "py/pro/l01": pass(noon)})
	snap.Badges["first-pass"] = noon
	after := Summarize(lib, snap, time.UTC)

	r := Diff(before, after, []string{"first-pass"})
	if r.XP != 100 || !r.LevelUp || r.Standing.Level != 2 {
		t.Errorf("reward: %+v", r)
	}
	if len(r.Badges) != 1 || r.Badges[0].Name != "Hello, World!" || !r.Badges[0].Earned {
		t.Errorf("reward badges: %+v", r.Badges)
	}
	if r := Diff(after, after, nil); r.XP != 0 || r.LevelUp || r.Badges == nil {
		t.Errorf("nothing changed: %+v", r)
	}
}

func TestBadgeIDsAreUnique(t *testing.T) {
	seen := map[string]bool{}
	for _, d := range defs(library()) {
		if seen[d.id] {
			t.Errorf("duplicate badge id %s", d.id)
		}
		seen[d.id] = true
		if d.name == "" || d.desc == "" || d.family == "" {
			t.Errorf("badge %s is missing a name, description or family", d.id)
		}
	}
}
