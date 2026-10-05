// Package profiles keeps the list of people using this box and hands out each
// one's progress store and workspace folder.
//
// A profile is picked, not logged into: anyone who can open the page can use
// any profile. It separates progress and files for a few people sharing one
// box; it is not access control. Cloudflare Access (see internal/access) is
// what decides who reaches the box at all.
package profiles

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
	"time"
	"unicode"
	"unicode/utf8"

	"github.com/eiyanproject/learnbox/internal/progress"
)

// DefaultID is the profile created on first start. It keeps the progress file
// and the ~/learn folder from before profiles existed, so nothing moves.
const DefaultID = "default"

// MaxProfiles keeps a typo-prone form from filling the disk with progress files.
const MaxProfiles = 20

var validID = regexp.MustCompile(`^[a-z0-9][a-z0-9-]{0,31}$`)

// ValidID reports whether id has the shape of a profile id. Ids end up in file
// names and paths, so anything read from a request is checked with this first.
func ValidID(id string) bool { return validID.MatchString(id) }

var (
	ErrNotFound = errors.New("no such profile")
	ErrBadName  = errors.New("a name is 1 to 40 characters, letters, digits, spaces and simple punctuation")
	ErrTooMany  = fmt.Errorf("at most %d profiles", MaxProfiles)
	ErrLastOne  = errors.New("the last profile cannot be deleted")
)

type Profile struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"created_at"`
}

type Registry struct {
	dir string

	mu     sync.Mutex
	list   []Profile
	stores map[string]*progress.Store
}

// Open loads profiles.json from dataDir, creating it with one default profile
// the first time.
func Open(dataDir string) (*Registry, error) {
	r := &Registry{dir: dataDir, stores: map[string]*progress.Store{}}
	raw, err := os.ReadFile(r.file())
	switch {
	case os.IsNotExist(err):
		r.list = []Profile{{ID: DefaultID, Name: "Learner", CreatedAt: time.Now().UTC()}}
		if err := r.save(); err != nil {
			return nil, err
		}
	case err != nil:
		return nil, err
	default:
		if err := json.Unmarshal(raw, &r.list); err != nil {
			return nil, fmt.Errorf("profiles.json: %w", err)
		}
	}
	return r, nil
}

func (r *Registry) file() string { return filepath.Join(r.dir, "profiles.json") }

func (r *Registry) List() []Profile {
	r.mu.Lock()
	defer r.mu.Unlock()
	return append([]Profile(nil), r.list...)
}

func (r *Registry) Get(id string) (Profile, bool) {
	r.mu.Lock()
	defer r.mu.Unlock()
	for _, p := range r.list {
		if p.ID == id {
			return p, true
		}
	}
	return Profile{}, false
}

// Create adds a profile. Its id is derived from the name, made unique.
func (r *Registry) Create(name string) (Profile, error) {
	name, err := cleanName(name)
	if err != nil {
		return Profile{}, err
	}
	r.mu.Lock()
	defer r.mu.Unlock()
	if len(r.list) >= MaxProfiles {
		return Profile{}, ErrTooMany
	}
	base := slug(name)
	id := base
	for n := 2; r.hasLocked(id); n++ {
		id = fmt.Sprintf("%s-%d", base, n)
	}
	p := Profile{ID: id, Name: name, CreatedAt: time.Now().UTC()}
	r.list = append(r.list, p)
	if err := r.save(); err != nil {
		r.list = r.list[:len(r.list)-1]
		return Profile{}, err
	}
	return p, nil
}

func (r *Registry) Rename(id, name string) (Profile, error) {
	name, err := cleanName(name)
	if err != nil {
		return Profile{}, err
	}
	r.mu.Lock()
	defer r.mu.Unlock()
	for i := range r.list {
		if r.list[i].ID == id {
			old := r.list[i].Name
			r.list[i].Name = name
			if err := r.save(); err != nil {
				r.list[i].Name = old
				return Profile{}, err
			}
			return r.list[i], nil
		}
	}
	return Profile{}, ErrNotFound
}

// Delete removes a profile and its progress file. Its lesson files are left
// on disk under WorkspaceBase(id): deleting someone's code is not something a
// profile list should do quietly.
func (r *Registry) Delete(id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	idx := -1
	for i, p := range r.list {
		if p.ID == id {
			idx = i
		}
	}
	if idx < 0 {
		return ErrNotFound
	}
	if len(r.list) == 1 {
		return ErrLastOne
	}
	kept := append(append([]Profile(nil), r.list[:idx]...), r.list[idx+1:]...)
	old := r.list
	r.list = kept
	if err := r.save(); err != nil {
		r.list = old
		return err
	}
	delete(r.stores, id)
	if err := os.Remove(r.progressPath(id)); err != nil && !os.IsNotExist(err) {
		return err
	}
	return nil
}

// Progress returns the profile's progress store, opening it on first use.
func (r *Registry) Progress(id string) (*progress.Store, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if !r.hasLocked(id) {
		return nil, ErrNotFound
	}
	if s := r.stores[id]; s != nil {
		return s, nil
	}
	s, err := progress.Open(r.progressPath(id))
	if err != nil {
		return nil, err
	}
	r.stores[id] = s
	return s, nil
}

func (r *Registry) progressPath(id string) string {
	if id == DefaultID {
		return filepath.Join(r.dir, "progress.json")
	}
	return filepath.Join(r.dir, "progress-"+id+".json")
}

// WorkspaceBase is where a profile's lesson folders live, relative to the
// learner's home. The default profile keeps ~/learn.
func WorkspaceBase(id string) string {
	if id == DefaultID {
		return "learn"
	}
	return path.Join("profiles", id, "learn")
}

func (r *Registry) hasLocked(id string) bool {
	for _, p := range r.list {
		if p.ID == id {
			return true
		}
	}
	return false
}

func (r *Registry) save() error {
	raw, err := json.MarshalIndent(r.list, "", "  ")
	if err != nil {
		return err
	}
	if err := os.MkdirAll(r.dir, 0o750); err != nil {
		return err
	}
	tmp := r.file() + ".tmp"
	if err := os.WriteFile(tmp, raw, 0o640); err != nil {
		return err
	}
	return os.Rename(tmp, r.file())
}

func cleanName(name string) (string, error) {
	name = strings.Join(strings.Fields(name), " ")
	if name == "" || utf8.RuneCountInString(name) > 40 {
		return "", ErrBadName
	}
	for _, c := range name {
		if !(unicode.IsLetter(c) || unicode.IsDigit(c) || c == ' ' || strings.ContainsRune("-_.'", c)) {
			return "", ErrBadName
		}
	}
	return name, nil
}

// slug turns a name into an id: lower-case ASCII letters and digits joined by
// single dashes. Names with no ASCII at all fall back to "player".
func slug(name string) string {
	var b strings.Builder
	dash := false
	for _, c := range strings.ToLower(name) {
		switch {
		case c >= 'a' && c <= 'z' || c >= '0' && c <= '9':
			b.WriteRune(c)
			dash = false
		case b.Len() > 0 && !dash:
			b.WriteByte('-')
			dash = true
		}
	}
	s := strings.Trim(b.String(), "-")
	if len(s) > 24 {
		s = strings.Trim(s[:24], "-")
	}
	if s == "" || s == DefaultID {
		s = "player"
	}
	return s
}
