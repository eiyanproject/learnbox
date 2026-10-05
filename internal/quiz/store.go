package quiz

import (
	"encoding/json"
	"os"
	"path/filepath"
	"sync"
	"time"
)

// Record is how one question has gone for one profile.
type Record struct {
	Right    int       `json:"right"`
	Wrong    int       `json:"wrong"`
	Streak   int       `json:"streak"` // right answers in a row since the last wrong one
	LastSeen time.Time `json:"last_seen,omitzero"`
}

// ClearAfter is how many right answers in a row take a question out of the
// mistakes review. One could be a lucky guess.
const ClearAfter = 2

// Mistake reports whether the question belongs in the mistakes review.
func (r Record) Mistake() bool { return r.Wrong > 0 && r.Streak < ClearAfter }

// Active is a mock exam in progress. Kept on disk so a reload resumes the same
// questions against the same clock rather than starting a fresh, easier one.
type Active struct {
	Exam     string    `json:"exam"`
	IDs      []string  `json:"ids"`
	Started  time.Time `json:"started"`
	Deadline time.Time `json:"deadline"`
}

// Result is a finished mock exam.
type Result struct {
	Track    string    `json:"track"`
	Exam     string    `json:"exam"`
	At       time.Time `json:"at"`
	Score    int       `json:"score"`
	Max      int       `json:"max"`
	Passed   bool      `json:"passed"`
	Seconds  int       `json:"seconds"`
	Overtime bool      `json:"overtime,omitempty"`
	Wrong    []string  `json:"wrong,omitempty"`
}

// MaxResults bounds the exam history kept per profile.
const MaxResults = 200

type data struct {
	// Questions is keyed track/question-id.
	Questions map[string]*Record `json:"questions"`
	// Active is keyed track/exam.
	Active  map[string]*Active `json:"active,omitempty"`
	Results []Result           `json:"results,omitempty"`
}

// Store is one profile's quiz record, a JSON file like the progress store.
type Store struct {
	path string
	mu   sync.Mutex
	d    data
}

func Open(path string) (*Store, error) {
	s := &Store{path: path, d: data{Questions: map[string]*Record{}}}
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
	if s.d.Questions == nil {
		s.d.Questions = map[string]*Record{}
	}
	return s, nil
}

func key(track, id string) string { return track + "/" + id }

// Records returns a copy of every question record for a track, keyed by id.
func (s *Store) Records(track string) map[string]Record {
	s.mu.Lock()
	defer s.mu.Unlock()
	out := map[string]Record{}
	prefix := track + "/"
	for k, r := range s.d.Questions {
		if len(k) > len(prefix) && k[:len(prefix)] == prefix {
			out[k[len(prefix):]] = *r
		}
	}
	return out
}

// Answered records answers to several questions at once and saves.
func (s *Store) Answered(track string, correct map[string]bool, now time.Time) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	for id, ok := range correct {
		r := s.d.Questions[key(track, id)]
		if r == nil {
			r = &Record{}
			s.d.Questions[key(track, id)] = r
		}
		if ok {
			r.Right++
			r.Streak++
		} else {
			r.Wrong++
			r.Streak = 0
		}
		r.LastSeen = now
	}
	return s.save()
}

// Active returns the running exam, if any.
func (s *Store) Active(track, exam string) (Active, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	a := s.d.Active[key(track, exam)]
	if a == nil {
		return Active{}, false
	}
	return *a, true
}

// Start records a new running exam, replacing any other for that exam.
func (s *Store) Start(track string, a Active) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.d.Active == nil {
		s.d.Active = map[string]*Active{}
	}
	s.d.Active[key(track, a.Exam)] = &a
	return s.save()
}

// Abandon drops a running exam without a result.
func (s *Store) Abandon(track, exam string) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	delete(s.d.Active, key(track, exam))
	return s.save()
}

// Finish ends a running exam: its result is kept, answers counted per
// question, and the exam no longer active.
func (s *Store) Finish(res Result, correct map[string]bool) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	for id, ok := range correct {
		r := s.d.Questions[key(res.Track, id)]
		if r == nil {
			r = &Record{}
			s.d.Questions[key(res.Track, id)] = r
		}
		if ok {
			r.Right++
			r.Streak++
		} else {
			r.Wrong++
			r.Streak = 0
		}
		r.LastSeen = res.At
	}
	delete(s.d.Active, key(res.Track, res.Exam))
	s.d.Results = append(s.d.Results, res)
	if over := len(s.d.Results) - MaxResults; over > 0 {
		s.d.Results = s.d.Results[over:]
	}
	return s.save()
}

// Results returns a track's exam history, newest first.
func (s *Store) Results(track string) []Result {
	s.mu.Lock()
	defer s.mu.Unlock()
	var out []Result
	for i := len(s.d.Results) - 1; i >= 0; i-- {
		if s.d.Results[i].Track == track {
			out = append(out, s.d.Results[i])
		}
	}
	return out
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
