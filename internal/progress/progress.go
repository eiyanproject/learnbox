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

type data struct {
	Lessons    map[string]*Entry `json:"lessons"`
	LastLesson string            `json:"last_lesson,omitempty"`
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
