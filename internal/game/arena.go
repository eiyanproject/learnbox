package game

import (
	"fmt"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/progress"
)

// The arena: each track's ladder of timed challenges, rounds then a boss.
//
//   - A challenge opens once the one before it in the ladder is won and its
//     own requirements - XP earned in the track, badges - are met.
//   - Starting it starts a clock. Pass the tests before the deadline and it
//     is won; run out of time, or forfeit, and it is lost.
//   - A loss starts a short cooldown before the next attempt.
//   - A win pays the challenge's XP plus up to half as much again for speed.
//     Winning it again only counts if it pays more than the best so far.
//
// The functions here decide; the caller supplies the time and does the saving.

// SpeedBonusPercent is the most a win can add to a challenge's XP, earned in
// proportion to the time left on the clock.
const SpeedBonusPercent = 50

// ChallengeXP is what a win pays: the base, plus the speed bonus scaled by
// the share of the time limit left unused.
func ChallengeXP(base int, limit, used time.Duration) int {
	if limit <= 0 {
		return base
	}
	left := min(max(limit-used, 0), limit)
	return base + int(int64(base)*SpeedBonusPercent*int64(left)/(100*int64(limit)))
}

// StartChallenge begins an attempt.
func StartChallenge(c *progress.Challenge, ch *content.Challenge, now time.Time) {
	c.Started = now
	c.Deadline = now.Add(time.Duration(ch.Minutes) * time.Minute)
}

// Expired reports whether an attempt is running past its deadline.
func Expired(c progress.Challenge, now time.Time) bool {
	return c.Active() && !now.Before(c.Deadline)
}

// LoseChallenge ends the running attempt as a loss and starts the cooldown.
func LoseChallenge(c *progress.Challenge, ch *content.Challenge, now time.Time) {
	c.Started, c.Deadline = time.Time{}, time.Time{}
	c.Losses++
	c.CooldownUntil = now.Add(time.Duration(ch.CooldownMinutes) * time.Minute)
}

// WinChallenge ends the running attempt as a win and returns what it paid.
func WinChallenge(c *progress.Challenge, ch *content.Challenge, now time.Time) int {
	limit := c.Deadline.Sub(c.Started)
	used := min(max(now.Sub(c.Started), 0), limit)
	xp := ChallengeXP(ch.XP, limit, used)

	if c.Wins == 0 {
		c.FirstWonAt = now
		c.LossesBeforeWin = c.Losses
	}
	c.Wins++
	secs := max(int(used/time.Second), 1)
	if c.BestSeconds == 0 || secs < c.BestSeconds {
		c.BestSeconds = secs
	}
	fraction := 100
	if limit > 0 {
		fraction = max(int(100*used/limit), 1)
	}
	if c.BestFraction == 0 || fraction < c.BestFraction {
		c.BestFraction = fraction
	}
	c.BestXP = max(c.BestXP, xp)
	c.Started, c.Deadline = time.Time{}, time.Time{}
	return xp
}

// Challenge states, as the arena shows them.
const (
	Locked   = "locked"
	Ready    = "ready"
	Active   = "active"
	Cooldown = "cooldown"
	Won      = "won" // and open to another go, for a better time
)

// ChallengeView is one challenge as one learner sees it.
type ChallengeView struct {
	ID              string `json:"id"`
	Title           string `json:"title"`
	Summary         string `json:"summary"`
	Boss            bool   `json:"boss"`
	Minutes         int    `json:"minutes"`
	CooldownMinutes int    `json:"cooldown_minutes"`
	XP              int    `json:"xp"`
	MaxXP           int    `json:"max_xp"`

	State string `json:"state"`
	// Locks says what still stands in the way of a locked challenge.
	Locks         []string  `json:"locks"`
	Deadline      time.Time `json:"deadline,omitzero"`
	CooldownUntil time.Time `json:"cooldown_until,omitzero"`

	Wins        int `json:"wins"`
	Losses      int `json:"losses"`
	BestSeconds int `json:"best_seconds,omitempty"`
	BestXP      int `json:"best_xp,omitempty"`
}

// CanStart reports whether an attempt may begin now.
func (v ChallengeView) CanStart() bool { return v.State == Ready || v.State == Won }

// Ladder is one track's challenges, in order.
type Ladder struct {
	Lang       string          `json:"lang"`
	Title      string          `json:"title"`
	TrackXP    int             `json:"track_xp"`
	Challenges []ChallengeView `json:"challenges"`
}

// Arena is every track's ladder. Tracks without one are left out.
func Arena(lib *content.Library, snap progress.Snapshot, loc *time.Location, now time.Time) []Ladder {
	st := compute(lib, snap, loc)
	names := map[string]string{}
	for _, d := range defs(lib) {
		names[d.id] = d.name
	}
	trackXP := map[string]int{}
	for _, t := range st.tracks {
		trackXP[t.Lang] = t.XP
	}

	out := []Ladder{}
	for _, t := range lib.Tracks {
		ladder := Ladder{Lang: t.Lang, Title: t.Title, TrackXP: trackXP[t.Lang], Challenges: []ChallengeView{}}
		var prev *content.Lesson
		for i := range t.Sections {
			if !t.Sections[i].Arena {
				continue
			}
			for _, l := range t.Sections[i].Lessons {
				ladder.Challenges = append(ladder.Challenges, view(l, prev, t, snap, names, ladder.TrackXP, now))
				prev = l
			}
		}
		if len(ladder.Challenges) > 0 {
			out = append(out, ladder)
		}
	}
	return out
}

// ChallengeFor finds one challenge's view.
func ChallengeFor(lib *content.Library, snap progress.Snapshot, loc *time.Location, now time.Time, id string) (ChallengeView, bool) {
	for _, ladder := range Arena(lib, snap, loc, now) {
		for _, c := range ladder.Challenges {
			if c.ID == id {
				return c, true
			}
		}
	}
	return ChallengeView{}, false
}

func view(l, prev *content.Lesson, t *content.Track, snap progress.Snapshot, names map[string]string, trackXP int, now time.Time) ChallengeView {
	ch, rec := l.Challenge, snap.Challenges[l.ID()]
	v := ChallengeView{
		ID: l.ID(), Title: l.Title, Summary: l.Summary, Boss: ch.Boss,
		Minutes: ch.Minutes, CooldownMinutes: ch.CooldownMinutes,
		XP: ch.XP, MaxXP: ch.XP + ch.XP*SpeedBonusPercent/100,
		Locks: []string{}, Wins: rec.Wins, Losses: rec.Losses,
		BestSeconds: rec.BestSeconds, BestXP: rec.BestXP,
	}

	if prev != nil && snap.Challenges[prev.ID()].Wins == 0 {
		v.Locks = append(v.Locks, fmt.Sprintf("Win %q first", prev.Title))
	}
	if need := ch.Requires.XP - trackXP; need > 0 {
		v.Locks = append(v.Locks, fmt.Sprintf("Earn %d more XP in %s (%d of %d)", need, t.Title, trackXP, ch.Requires.XP))
	}
	for _, id := range ch.Requires.Badges {
		if _, ok := snap.Badges[id]; !ok {
			name := names[id]
			if name == "" {
				name = id
			}
			v.Locks = append(v.Locks, fmt.Sprintf("Earn the badge %q", name))
		}
	}

	switch {
	case rec.Active() && now.Before(rec.Deadline):
		v.State, v.Deadline = Active, rec.Deadline
	case rec.Wins == 0 && len(v.Locks) > 0:
		v.State = Locked
	case now.Before(rec.CooldownUntil):
		v.State, v.CooldownUntil = Cooldown, rec.CooldownUntil
	case rec.Wins > 0:
		v.State = Won
	default:
		v.State = Ready
	}
	if v.State != Locked {
		v.Locks = []string{} // once in, a requirement that moved does not lock it again
	}
	return v
}

// Validate reports content the rules cannot honour: a challenge that asks
// for a badge nobody can earn would stay locked for ever.
func Validate(lib *content.Library) error {
	known := map[string]bool{}
	for _, d := range defs(lib) {
		known[d.id] = true
	}
	for _, t := range lib.Tracks {
		for _, sec := range t.Sections {
			for _, l := range sec.Lessons {
				if l.Challenge == nil {
					continue
				}
				for _, id := range l.Challenge.Requires.Badges {
					if !known[id] {
						return fmt.Errorf("%s: challenge requires unknown badge %q", l.ID(), id)
					}
				}
			}
		}
	}
	return nil
}
