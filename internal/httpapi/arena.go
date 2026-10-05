package httpapi

import (
	"net/http"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/game"
	"github.com/eiyanproject/learnbox/internal/progress"
)

// The arena's clock is the server's. A challenge's text, files and shell are
// handed out only while an attempt runs (or once it has been won), so the
// time on the clock is the time spent on the problem.

// settle turns an attempt that has run past its deadline into the loss it
// is. Nothing watches the clock; whoever looks next finds it settled.
func (s *Server) settle(v *viewer, l *content.Lesson, now time.Time) error {
	if l.Challenge == nil || !game.Expired(v.Progress.Challenge(l.ID()), now) {
		return nil
	}
	_, err := v.Progress.UpdateChallenge(l.ID(), func(c *progress.Challenge) {
		if game.Expired(*c, now) {
			game.LoseChallenge(c, l.Challenge, c.Deadline) // the cooldown runs from when time ran out
			s.challenges.WithLabelValues(l.Lang, "timeout").Inc()
		}
	})
	return err
}

func (s *Server) settleAll(v *viewer, now time.Time) error {
	for id, c := range v.Progress.Snapshot().Challenges {
		if !game.Expired(c, now) {
			continue
		}
		if l := s.Lib.Lesson(id); l != nil {
			if err := s.settle(v, l, now); err != nil {
				return err
			}
		}
	}
	return nil
}

// challengeView settles l and returns how it stands for the viewer.
func (s *Server) challengeView(v *viewer, l *content.Lesson, now time.Time) (game.ChallengeView, error) {
	if err := s.settle(v, l, now); err != nil {
		return game.ChallengeView{}, err
	}
	cv, _ := game.ChallengeFor(s.Lib, v.Progress.Snapshot(), s.location(), now, l.ID())
	return cv, nil
}

// challengeOpen reports whether the viewer may see and touch l's workspace:
// always for an ordinary lesson, and for a challenge only during an attempt
// or after a win. Otherwise it answers 409 "challenge_not_started".
func (s *Server) challengeOpen(w http.ResponseWriter, v *viewer, l *content.Lesson) bool {
	if l.Challenge == nil {
		return true
	}
	cv, err := s.challengeView(v, l, time.Now())
	if err != nil {
		s.fail(w, "progress", err)
		return false
	}
	if cv.State == game.Active || cv.Wins > 0 {
		return true
	}
	writeJSON(w, http.StatusConflict, map[string]any{
		"error": "start this challenge from the arena first", "code": "challenge_not_started", "challenge": cv,
	})
	return false
}

func (s *Server) arena(w http.ResponseWriter, r *http.Request) {
	v := s.who(w, r)
	if v == nil {
		return
	}
	now := time.Now()
	if err := s.settleAll(v, now); err != nil {
		s.fail(w, "progress", err)
		return
	}
	// Badges are a requirement here, so record any that are due first.
	if _, _, err := s.standings(v); err != nil {
		s.fail(w, "progress", err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{
		"now":     now.UTC(),
		"ladders": game.Arena(s.Lib, v.Progress.Snapshot(), s.location(), now),
	})
}

func (s *Server) challengeFrom(w http.ResponseWriter, r *http.Request) *content.Lesson {
	l := s.lessonFrom(w, r)
	if l != nil && l.Challenge == nil {
		writeErr(w, http.StatusNotFound, "not an arena challenge")
		return nil
	}
	return l
}

func (s *Server) startChallenge(w http.ResponseWriter, r *http.Request) {
	l := s.challengeFrom(w, r)
	if l == nil {
		return
	}
	if err := s.diskHeadroom(); err != nil {
		s.errs.WithLabelValues("disk_full").Inc()
		writeErr(w, http.StatusInsufficientStorage, err.Error())
		return
	}
	v := s.who(w, r)
	if v == nil {
		return
	}
	if _, _, err := s.standings(v); err != nil {
		s.fail(w, "progress", err)
		return
	}
	now := time.Now()
	cv, err := s.challengeView(v, l, now)
	if err != nil {
		s.fail(w, "progress", err)
		return
	}
	switch cv.State {
	case game.Active:
		// A second press, or a second tab: the attempt is already running.
		writeJSON(w, http.StatusOK, map[string]any{"now": now.UTC(), "challenge": cv})
		return
	case game.Locked:
		writeJSON(w, http.StatusForbidden, map[string]any{"error": "this challenge is locked", "code": "challenge_locked", "challenge": cv})
		return
	case game.Cooldown:
		writeJSON(w, http.StatusConflict, map[string]any{"error": "cooling down after a loss", "code": "challenge_cooldown", "challenge": cv})
		return
	}

	// Every attempt starts from the starter files, with a fresh shell.
	s.Terms.Kill(v.sessionKey("lesson/" + l.ID()))
	if _, err := v.WS.Reset(l); err != nil {
		s.fail(w, "workspace", err)
		return
	}
	now = time.Now() // the reset is not on the learner's clock
	if _, err := v.Progress.UpdateChallenge(l.ID(), func(c *progress.Challenge) {
		game.StartChallenge(c, l.Challenge, now)
	}); err != nil {
		s.fail(w, "progress", err)
		return
	}
	s.challenges.WithLabelValues(l.Lang, "started").Inc()
	cv, err = s.challengeView(v, l, now)
	if err != nil {
		s.fail(w, "progress", err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"now": now.UTC(), "challenge": cv})
}

func (s *Server) forfeitChallenge(w http.ResponseWriter, r *http.Request) {
	l := s.challengeFrom(w, r)
	if l == nil {
		return
	}
	v := s.who(w, r)
	if v == nil {
		return
	}
	now := time.Now()
	if err := s.settle(v, l, now); err != nil {
		s.fail(w, "progress", err)
		return
	}
	if _, err := v.Progress.UpdateChallenge(l.ID(), func(c *progress.Challenge) {
		if c.Active() {
			game.LoseChallenge(c, l.Challenge, now)
			s.challenges.WithLabelValues(l.Lang, "forfeit").Inc()
		}
	}); err != nil {
		s.fail(w, "progress", err)
		return
	}
	cv, err := s.challengeView(v, l, now)
	if err != nil {
		s.fail(w, "progress", err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"now": now.UTC(), "challenge": cv})
}

// checkChallenge is Check for an arena lesson. received is when the request
// arrived: a check sent in time counts even if its tests finish after the
// deadline.
func (s *Server) checkChallenge(w http.ResponseWriter, r *http.Request, v *viewer, l *content.Lesson, received time.Time) {
	cv, err := s.challengeView(v, l, received)
	if err != nil {
		s.fail(w, "progress", err)
		return
	}
	respond := func(res any, outcome string, reward game.Reward, xp int) {
		cv, err := s.challengeView(v, l, time.Now())
		if err != nil {
			s.fail(w, "progress", err)
			return
		}
		status := progress.Started
		if cv.Wins > 0 {
			status = progress.Passed
		}
		writeJSON(w, http.StatusOK, map[string]any{
			"result": res, "status": status, "attempts": cv.Wins + cv.Losses, "reward": reward,
			"now": time.Now().UTC(), "challenge": cv, "outcome": outcome, "challenge_xp": xp,
		})
	}

	before, _, err := s.standings(v)
	if err != nil {
		s.fail(w, "progress", err)
		return
	}
	if cv.State != game.Active {
		if cv.Wins == 0 {
			if cv.State != game.Cooldown {
				writeJSON(w, http.StatusConflict, map[string]any{
					"error": "start this challenge from the arena first", "code": "challenge_not_started", "challenge": cv,
				})
				return
			}
			// Time ran out, and settling it just now recorded the loss.
			respond(nil, "lost", game.Diff(before, before, nil), 0)
			return
		}
		// Won already and no clock running: a practice run, for nothing.
		res, err := s.Runner.CheckDir(r.Context(), l, v.WS.Rel(l))
		if err != nil {
			s.fail(w, "check", err)
			return
		}
		s.checks.WithLabelValues(l.Lang, res.Status).Inc()
		respond(res, "", game.Diff(before, before, nil), 0)
		return
	}

	res, err := s.Runner.CheckDir(r.Context(), l, v.WS.Rel(l))
	if err != nil {
		s.fail(w, "check", err)
		return
	}
	s.checks.WithLabelValues(l.Lang, res.Status).Inc()
	if !res.Passed {
		respond(res, "", game.Diff(before, before, nil), 0) // the clock keeps running
		return
	}
	xp := 0
	if _, err := v.Progress.UpdateChallenge(l.ID(), func(c *progress.Challenge) {
		if c.Active() {
			xp = game.WinChallenge(c, l.Challenge, received)
		}
	}); err != nil {
		s.fail(w, "progress", err)
		return
	}
	s.challenges.WithLabelValues(l.Lang, "won").Inc()
	after, fresh, err := s.standings(v)
	if err != nil {
		s.fail(w, "progress", err)
		return
	}
	respond(res, "won", game.Diff(before, after, fresh), xp)
}
