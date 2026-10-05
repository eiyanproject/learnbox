package httpapi

import (
	"net/http"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/game"
	"github.com/eiyanproject/learnbox/internal/progress"
)

// location is the timezone days are counted in, for streaks and the badges
// about when a lesson was passed.
func (s *Server) location() *time.Location {
	if s.Location != nil {
		return s.Location
	}
	return time.Local
}

// standings records any badge the viewer now qualifies for and returns the
// summary after that, with the ids of the badges this call recorded.
func (s *Server) standings(v *viewer) (game.Summary, []string, error) {
	loc := s.location()
	fresh, err := v.Progress.AwardBadges(game.Qualified(s.Lib, v.Progress.Snapshot(), loc), time.Now().UTC())
	if err != nil {
		return game.Summary{}, nil, err
	}
	return game.Summarize(s.Lib, v.Progress.Snapshot(), loc), fresh, nil
}

// summary is the viewer's XP, level and badges. Asking for it is also what
// records badges for lessons passed before badges existed, so they arrive
// here, quietly, rather than all at once with the next check.
func (s *Server) summary(w http.ResponseWriter, r *http.Request) {
	v := s.who(w, r)
	if v == nil {
		return
	}
	sum, _, err := s.standings(v)
	if err != nil {
		s.fail(w, "progress", err)
		return
	}
	writeJSON(w, http.StatusOK, sum)
}

// worth is what a lesson pays in full, what it pays this learner now, and
// what revealing one more hint would take off that.
func (s *Server) worth(l *content.Lesson, e progress.Entry) (full, now, hintCost int) {
	full, now, ok := game.Worth(s.Lib, l, e)
	if ok && e.Status != progress.Passed && e.HintsRevealed < len(l.Hints) {
		hintCost = now - game.AfterHints(full, game.PaidHints(e)+1)
	}
	return full, now, hintCost
}
