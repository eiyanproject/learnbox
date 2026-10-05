// Package progress stores per-lesson progress in one JSON file. One learner
// and a few hundred lessons at most: a database would be all overhead.
package progress

import (
	"encoding/json"
	"os"
	"path/filepath"
	"sync"
	"time"
)

type Status string

const (
	NotStarted Status = ""
	Started    Status = "started"
	Passed     Status = "passed"
)

type Entry struct {
	Status        Status    `json:"status"`
	HintsRevealed int       `json:"hints_revealed"`
	Attempts      int       `json:"attempts"`
	FirstOpened   time.Time `json:"first_opened,omitzero"`
	LastOpened    time.Time `json:"last_opened,omitzero"`
	PassedAt      time.Time `json:"passed_at,omitzero"`
}

// Challenge is the record of one arena challenge: the attempt in progress,
// if any, and every result so far.
type Challenge struct {
	// Started and Deadline are set while an attempt is running and cleared
	// when it ends. The clock is the server's, so a reload cannot reset it.
	Started  time.Time `json:"started,omitzero"`
	Deadline time.Time `json:"deadline,omitzero"`

	Wins          int       `json:"wins"`
	Losses        int       `json:"losses"`
	CooldownUntil time.Time `json:"cooldown_until,omitzero"`
	FirstWonAt    time.Time `json:"first_won_at,omitzero"`
	// LossesBeforeWin is how many attempts were lost before the first win.
	LossesBeforeWin int `json:"losses_before_win,omitempty"`
	BestSeconds     int `json:"best_seconds,omitempty"`
	BestXP          int `json:"best_xp,omitempty"`
	// BestFraction is the share of the time limit the fastest win used, in
	// percent; it decides the speed badge.
	BestFraction int `json:"best_fraction,omitempty"`
}

// Active reports whether an attempt is running.
func (c Challenge) Active() bool { return !c.Started.IsZero() }

type data struct {
	Lessons    map[string]*Entry     `json:"lessons"`
	LastLesson string                `json:"last_lesson,omitempty"`
	Challenges map[string]*Challenge `json:"challenges,omitempty"`
	// Badges records when each badge was first earned. Kept once earned, so a
	// badge does not vanish if the lessons behind it change later.
	Badges map[string]time.Time `json:"badges,omitempty"`
}

// Snapshot is a copy of everything in the store, for computing XP and badges.
type Snapshot struct {
	Lessons    map[string]Entry
	Challenges map[string]Challenge
	Badges     map[string]time.Time
}

type Store struct {
	path string
	mu   sync.Mutex
	d    data
}

func Open(path string) (*Store, error) {
	s := &Store{path: path, d: data{Lessons: map[string]*Entry{}}}
	raw, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return s, nil
	}
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(raw, &s.d); err != nil {
		return nil, err
	}
	if s.d.Lessons == nil {
		s.d.Lessons = map[string]*Entry{}
	}
	return s, nil
}

// Snapshot copies the whole store.
func (s *Store) Snapshot() Snapshot {
	s.mu.Lock()
	defer s.mu.Unlock()
	out := Snapshot{
		Lessons:    make(map[string]Entry, len(s.d.Lessons)),
		Challenges: make(map[string]Challenge, len(s.d.Challenges)),
		Badges:     make(map[string]time.Time, len(s.d.Badges)),
	}
	for k, v := range s.d.Lessons {
		out.Lessons[k] = *v
	}
	for k, v := range s.d.Challenges {
		out.Challenges[k] = *v
	}
	for k, v := range s.d.Badges {
		out.Badges[k] = v
	}
	return out
}

// Challenge returns one challenge's record.
func (s *Store) Challenge(id string) Challenge {
	s.mu.Lock()
	defer s.mu.Unlock()
	if c := s.d.Challenges[id]; c != nil {
		return *c
	}
	return Challenge{}
}

// UpdateChallenge applies fn to a challenge's record and saves.
func (s *Store) UpdateChallenge(id string, fn func(c *Challenge)) (Challenge, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.d.Challenges == nil {
		s.d.Challenges = map[string]*Challenge{}
	}
	c := s.d.Challenges[id]
	if c == nil {
		c = &Challenge{}
		s.d.Challenges[id] = c
	}
	fn(c)
	return *c, s.save()
}

// AwardBadges records the badges in ids that were not already earned, stamped
// with now, and returns just those.
func (s *Store) AwardBadges(ids []string, now time.Time) ([]string, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.d.Badges == nil {
		s.d.Badges = map[string]time.Time{}
	}
	var fresh []string
	for _, id := range ids {
		if _, ok := s.d.Badges[id]; !ok {
			s.d.Badges[id] = now
			fresh = append(fresh, id)
		}
	}
	if len(fresh) == 0 {
		return nil, nil
	}
	return fresh, s.save()
}

func (s *Store) Get(id string) Entry {
	s.mu.Lock()
	defer s.mu.Unlock()
	if e := s.d.Lessons[id]; e != nil {
		return *e
	}
	return Entry{}
}

func (s *Store) All() (map[string]Entry, string) {
	s.mu.Lock()
	defer s.mu.Unlock()
	out := make(map[string]Entry, len(s.d.Lessons))
	for k, v := range s.d.Lessons {
		out[k] = *v
	}
	return out, s.d.LastLesson
}

// Update applies fn to the lesson's entry and saves.
func (s *Store) Update(id string, fn func(e *Entry)) (Entry, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	e := s.d.Lessons[id]
	if e == nil {
		e = &Entry{}
		s.d.Lessons[id] = e
	}
	fn(e)
	return *e, s.save()
}

func (s *Store) Opened(id string) (Entry, error) {
	s.mu.Lock()
	s.d.LastLesson = id
	s.mu.Unlock()
	return s.Update(id, func(e *Entry) {
		now := time.Now().UTC()
		if e.FirstOpened.IsZero() {
			e.FirstOpened = now
		}
		e.LastOpened = now
		if e.Status == NotStarted {
			e.Status = Started
		}
	})
}

func (s *Store) save() error {
	raw, err := json.MarshalIndent(s.d, "", "  ")
	if err != nil {
		return err
	}
	if err := os.MkdirAll(filepath.Dir(s.path), 0o750); err != nil {
		return err
	}
	tmp := s.path + ".tmp"
	if err := os.WriteFile(tmp, raw, 0o640); err != nil {
		return err
	}
	return os.Rename(tmp, s.path)
}
