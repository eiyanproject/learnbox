// Package game turns a progress snapshot into XP, a level and badges.
//
// Everything here is a pure function of the lessons that exist and what the
// learner has done: no clock, no storage. That is what lets lessons passed
// before the feature existed count, and what makes the rules testable.
//
// The rules:
//
//   - A passed lesson is worth its section's xp (track.yaml, default 100). A
//     lesson with a difficulty rating - the imported practice exercises - is
//     worth 10 XP per point instead.
//   - Each hint revealed before the pass takes 10% off, down to half. Hints
//     read afterwards are free.
//   - An arena win is worth what was recorded when it was won.
//   - Level n starts at 50*n*(n-1) XP: each level is 100 XP longer than the
//     last.
package game

import (
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/progress"
)

const (
	DefaultLessonXP  = 100
	XPPerDifficulty  = 10
	HintCostPercent  = 10
	HintFloorPercent = 50
)

// LessonXP is what passing l pays with no hints revealed.
func LessonXP(sec *content.Section, l *content.Lesson) int {
	if l.Difficulty > 0 {
		return XPPerDifficulty * min(l.Difficulty, 10)
	}
	if sec.XP > 0 {
		return sec.XP
	}
	return DefaultLessonXP
}

// AfterHints applies the cost of the hints that were paid for.
func AfterHints(full, paidHints int) int {
	return full * max(100-HintCostPercent*paidHints, HintFloorPercent) / 100
}

// PaidHints is how many of an entry's hints count against its XP.
func PaidHints(e progress.Entry) int {
	return max(e.HintsRevealed-e.FreeHints, 0)
}

// Worth reports what the lesson pays in full and what it pays this learner,
// given the hints they have revealed. ok is false for a lesson the library
// does not have, or an arena challenge, which is paid by its own rules.
func Worth(lib *content.Library, l *content.Lesson, e progress.Entry) (full, now int, ok bool) {
	for _, t := range lib.Tracks {
		if t.Lang != l.Lang {
			continue
		}
		for i := range t.Sections {
			sec := &t.Sections[i]
			if sec.ID != l.Section || sec.Arena {
				continue
			}
			full = LessonXP(sec, l)
			return full, AfterHints(full, PaidHints(e)), true
		}
	}
	return 0, 0, false
}

// LevelFloor is the total XP at which level n starts.
func LevelFloor(n int) int { return 50 * n * (n - 1) }

// LevelFor is the level a total XP has reached. Levels start at 1.
func LevelFor(xp int) int {
	n := 1
	for LevelFloor(n+1) <= xp {
		n++
	}
	return n
}

var titles = []struct {
	from int
	name string
}{
	{40, "Legend"},
	{30, "Wizard"},
	{25, "Architect"},
	{20, "Engineer"},
	{15, "Builder"},
	{10, "Apprentice"},
	{5, "Tinkerer"},
	{1, "Newcomer"},
}

// TitleFor is the rank shown beside a level.
func TitleFor(level int) string {
	for _, t := range titles {
		if level >= t.from {
			return t.name
		}
	}
	return titles[len(titles)-1].name
}

// Standing is where a learner stands: the part of a summary the top bar shows.
type Standing struct {
	XP    int    `json:"xp"`
	Level int    `json:"level"`
	Title string `json:"title"`
	// LevelFloor and NextLevel are the XP totals this level and the next
	// start at, for drawing the bar between them.
	LevelFloor int `json:"level_floor"`
	NextLevel  int `json:"next_level"`
}

func standing(xp int) Standing {
	lv := LevelFor(xp)
	return Standing{XP: xp, Level: lv, Title: TitleFor(lv), LevelFloor: LevelFloor(lv), NextLevel: LevelFloor(lv + 1)}
}

type TrackXP struct {
	Lang  string `json:"lang"`
	Title string `json:"title"`
	XP    int    `json:"xp"`
	// Possible is what the track's lessons pay in total with no hints used.
	Possible int `json:"possible"`
}

type Summary struct {
	Standing
	Passed int       `json:"passed"`
	Tracks []TrackXP `json:"tracks"`
	Badges []Badge   `json:"badges"`
}

// Reward is what one check changed.
type Reward struct {
	XP       int      `json:"xp"`
	LevelUp  bool     `json:"level_up"`
	Badges   []Badge  `json:"badges"`
	Standing Standing `json:"standing"`
}

// Summarize computes the whole summary. A badge shows as earned only when the
// snapshot records it: earning is an event with a date, written down by the
// caller (see Qualified), so a badge survives the lessons behind it changing.
func Summarize(lib *content.Library, snap progress.Snapshot, loc *time.Location) Summary {
	st := compute(lib, snap, loc)
	sum := Summary{Standing: standing(st.xp), Passed: st.passed, Tracks: st.tracks, Badges: []Badge{}}
	for _, d := range defs(lib) {
		at, earned := snap.Badges[d.id]
		sum.Badges = append(sum.Badges, d.badge(st, earned, at))
	}
	return sum
}

// Qualified lists the ids of every badge the snapshot meets the bar for,
// whether or not it is recorded as earned yet.
func Qualified(lib *content.Library, snap progress.Snapshot, loc *time.Location) []string {
	st := compute(lib, snap, loc)
	var ids []string
	for _, d := range defs(lib) {
		if have, want := d.progress(st); have >= want {
			ids = append(ids, d.id)
		}
	}
	return ids
}

// Diff builds the reward for whatever happened between two summaries. fresh
// holds the ids of the badges first recorded in between.
func Diff(before, after Summary, fresh []string) Reward {
	r := Reward{
		XP:       after.XP - before.XP,
		LevelUp:  after.Level > before.Level,
		Badges:   []Badge{},
		Standing: after.Standing,
	}
	for _, id := range fresh {
		for _, b := range after.Badges {
			if b.ID == id {
				r.Badges = append(r.Badges, b)
			}
		}
	}
	return r
}

// ---------- the numbers badges are decided from ----------

type trackStats struct {
	guided, guidedPassed int
}

type stats struct {
	xp     int
	level  int
	tracks []TrackXP
	byLang map[string]*trackStats

	passed         int // lessons, of any kind
	practicePassed int
	tracksTouched  int // tracks with a passed lesson
	tracksTotal    int // tracks with any lesson to pass

	sectionsDone   int
	beginnerDone   int
	noHintSections int

	firstTry    int
	maxAttempts int // most attempts any pass needed
	lucky13     bool
	allHints    bool

	streak    int // longest run of days with a pass
	bestDay   int // most passes in one day
	nightOwl  bool
	earlyBird bool
	weekend   bool
	newYear   bool
	speedrun  bool
}

// noHintSectionMin is how many lessons of a section must offer hints before
// finishing it without any is worth a badge.
const noHintSectionMin = 3

func compute(lib *content.Library, snap progress.Snapshot, loc *time.Location) *stats {
	if loc == nil {
		loc = time.UTC
	}
	st := &stats{byLang: map[string]*trackStats{}}
	days := map[int64]int{}
	mark := func(at time.Time) {
		if at.IsZero() {
			return
		}
		t := at.In(loc)
		y, m, d := t.Date()
		day := time.Date(y, m, d, 0, 0, 0, 0, time.UTC).Unix() / 86400
		days[day]++
		switch h := t.Hour(); {
		case h < 5:
			st.nightOwl = true
		case h < 7:
			st.earlyBird = true
		}
		if m == time.January && d == 1 {
			st.newYear = true
		}
	}

	for _, t := range lib.Tracks {
		ts := &trackStats{}
		st.byLang[t.Lang] = ts
		tx := TrackXP{Lang: t.Lang, Title: t.Title}
		lessons, touched := 0, false

		for i := range t.Sections {
			sec := &t.Sections[i]
			if sec.Arena {
				for _, l := range sec.Lessons {
					if c := snap.Challenges[l.ID()]; c.Wins > 0 {
						tx.XP += c.BestXP
						mark(c.FirstWonAt)
					}
				}
				continue
			}

			testable, done, hinted, paid := 0, 0, 0, 0
			for _, l := range sec.Lessons {
				if !l.HasTest {
					continue
				}
				testable++
				full := LessonXP(sec, l)
				tx.Possible += full
				guided := l.Difficulty == 0
				if guided {
					ts.guided++
				}
				if len(l.Hints) > 0 {
					hinted++
				}
				e := snap.Lessons[l.ID()]
				if e.Status != progress.Passed {
					continue
				}
				done++
				touched = true
				st.passed++
				if guided {
					ts.guidedPassed++
				} else {
					st.practicePassed++
				}
				hints := PaidHints(e)
				paid += hints
				tx.XP += AfterHints(full, hints)
				if len(l.Hints) > 0 && hints >= len(l.Hints) {
					st.allHints = true
				}

				attempts := e.PassAttempts
				if attempts == 0 {
					attempts = e.Attempts // passed before the attempt was recorded
				}
				if attempts == 1 {
					st.firstTry++
				}
				if attempts == 13 {
					st.lucky13 = true
				}
				st.maxAttempts = max(st.maxAttempts, attempts)

				mark(e.PassedAt)
				if !e.FirstOpened.IsZero() && !e.PassedAt.Before(e.FirstOpened) && e.PassedAt.Sub(e.FirstOpened) < 2*time.Minute {
					st.speedrun = true
				}
			}
			lessons += testable
			if testable > 0 && done == testable {
				st.sectionsDone++
				if sec.Beginner {
					st.beginnerDone++
				}
				if paid == 0 && hinted >= noHintSectionMin {
					st.noHintSections++
				}
			}
		}

		if lessons > 0 {
			st.tracksTotal++
		}
		if touched {
			st.tracksTouched++
		}
		st.xp += tx.XP
		st.tracks = append(st.tracks, tx)
	}

	for day, n := range days {
		st.bestDay = max(st.bestDay, n)
		// Day 0 was a Thursday, so day%7 == 2 is a Saturday.
		if day%7 == 2 && days[day+1] > 0 {
			st.weekend = true
		}
		if days[day-1] > 0 {
			continue // not the first day of its run
		}
		run := 1
		for days[day+int64(run)] > 0 {
			run++
		}
		st.streak = max(st.streak, run)
	}

	st.level = LevelFor(st.xp)
	return st
}
