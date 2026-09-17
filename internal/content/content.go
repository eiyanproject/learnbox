// Package content loads tracks and lessons from disk.
//
// Layout (under each content root):
//
//	<lang>/track.yaml
//	<lang>/<section>/<slug>/lesson.md   front matter + Markdown explanation
//	<lang>/<section>/<slug>/starter/    copied into the learner's workspace
//	<lang>/<section>/<slug>/tests/      hidden tests, added only at check time
//	<lang>/<section>/<slug>/solution/   reference answer, used by `learnbox verify`, never served
//
// Several roots are merged: the repo's hand-written lessons and the generated
// Exercism import both use this layout.
package content

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"gopkg.in/yaml.v3"
)

type Track struct {
	Lang        string    `yaml:"-" json:"lang"`
	Title       string    `yaml:"title" json:"title"`
	Description string    `yaml:"description" json:"description"`
	Order       int       `yaml:"order" json:"-"`
	Sections    []Section `yaml:"sections" json:"sections"`
}

type Section struct {
	ID          string    `yaml:"id" json:"id"`
	Title       string    `yaml:"title" json:"title"`
	Description string    `yaml:"description" json:"description"`
	Lessons     []*Lesson `yaml:"-" json:"lessons"`
}

type Lesson struct {
	Lang    string `yaml:"-" json:"lang"`
	Section string `yaml:"-" json:"section"`
	Slug    string `yaml:"-" json:"slug"`

	Title      string   `yaml:"title" json:"title"`
	Summary    string   `yaml:"summary" json:"summary"`
	Order      int      `yaml:"order" json:"-"`
	Difficulty int      `yaml:"difficulty" json:"difficulty,omitempty"`
	Files      []string `yaml:"files" json:"files"`
	Run        string   `yaml:"run" json:"run,omitempty"`
	Hints      []string `yaml:"hints" json:"-"`
	Source     string   `yaml:"source" json:"source,omitempty"` // attribution, Markdown

	Dir     string `yaml:"-" json:"-"`
	Body    string `yaml:"-" json:"-"` // Markdown
	HasTest bool   `yaml:"-" json:"has_tests"`
}

// ID is lang/section/slug, the key used everywhere else.
func (l *Lesson) ID() string { return l.Lang + "/" + l.Section + "/" + l.Slug }

func (l *Lesson) StarterDir() string  { return filepath.Join(l.Dir, "starter") }
func (l *Lesson) TestsDir() string    { return filepath.Join(l.Dir, "tests") }
func (l *Lesson) SolutionDir() string { return filepath.Join(l.Dir, "solution") }

type Library struct {
	Tracks  []*Track
	lessons map[string]*Lesson
}

func (lib *Library) Lesson(id string) *Lesson { return lib.lessons[id] }

// Neighbours returns the lessons before and after id within its section.
func (lib *Library) Neighbours(id string) (prev, next *Lesson) {
	l := lib.lessons[id]
	if l == nil {
		return nil, nil
	}
	for _, t := range lib.Tracks {
		if t.Lang != l.Lang {
			continue
		}
		for _, s := range t.Sections {
			if s.ID != l.Section {
				continue
			}
			for i, x := range s.Lessons {
				if x == l {
					if i > 0 {
						prev = s.Lessons[i-1]
					}
					if i+1 < len(s.Lessons) {
						next = s.Lessons[i+1]
					}
				}
			}
		}
	}
	return prev, next
}

// Load reads every root. Later roots add sections and lessons to tracks
// defined earlier; a root may also define a track of its own.
func Load(roots ...string) (*Library, error) {
	lib := &Library{lessons: map[string]*Lesson{}}
	tracks := map[string]*Track{}

	for _, root := range roots {
		langs, err := os.ReadDir(root)
		if os.IsNotExist(err) {
			continue
		}
		if err != nil {
			return nil, err
		}
		for _, ld := range langs {
			if !ld.IsDir() || strings.HasPrefix(ld.Name(), ".") {
				continue
			}
			lang := ld.Name()
			langDir := filepath.Join(root, lang)

			if raw, err := os.ReadFile(filepath.Join(langDir, "track.yaml")); err == nil {
				var t Track
				if err := yaml.Unmarshal(raw, &t); err != nil {
					return nil, fmt.Errorf("%s/track.yaml: %w", langDir, err)
				}
				t.Lang = lang
				if prev, ok := tracks[lang]; ok {
					mergeSections(prev, t.Sections)
				} else {
					tracks[lang] = &t
				}
			}
			t := tracks[lang]
			if t == nil {
				return nil, fmt.Errorf("%s has lessons but no track.yaml in any root", langDir)
			}

			for i := range t.Sections {
				sec := &t.Sections[i]
				dirs, err := os.ReadDir(filepath.Join(langDir, sec.ID))
				if err != nil {
					continue
				}
				for _, d := range dirs {
					if !d.IsDir() {
						continue
					}
					l, err := loadLesson(filepath.Join(langDir, sec.ID, d.Name()))
					if err != nil {
						return nil, err
					}
					l.Lang, l.Section, l.Slug = lang, sec.ID, d.Name()
					if _, dup := lib.lessons[l.ID()]; dup {
						return nil, fmt.Errorf("duplicate lesson %s", l.ID())
					}
					lib.lessons[l.ID()] = l
					sec.Lessons = append(sec.Lessons, l)
				}
			}
		}
	}

	for _, t := range tracks {
		for i := range t.Sections {
			ls := t.Sections[i].Lessons
			sort.SliceStable(ls, func(a, b int) bool {
				if ls[a].Order != ls[b].Order {
					return ls[a].Order < ls[b].Order
				}
				if ls[a].Difficulty != ls[b].Difficulty {
					return ls[a].Difficulty < ls[b].Difficulty
				}
				return ls[a].Slug < ls[b].Slug
			})
		}
		lib.Tracks = append(lib.Tracks, t)
	}
	sort.Slice(lib.Tracks, func(a, b int) bool {
		if lib.Tracks[a].Order != lib.Tracks[b].Order {
			return lib.Tracks[a].Order < lib.Tracks[b].Order
		}
		return lib.Tracks[a].Lang < lib.Tracks[b].Lang
	})
	return lib, nil
}

func mergeSections(t *Track, extra []Section) {
	for _, s := range extra {
		found := false
		for _, have := range t.Sections {
			if have.ID == s.ID {
				found = true
				break
			}
		}
		if !found {
			t.Sections = append(t.Sections, s)
		}
	}
}

func loadLesson(dir string) (*Lesson, error) {
	raw, err := os.ReadFile(filepath.Join(dir, "lesson.md"))
	if err != nil {
		return nil, err
	}
	front, body, err := splitFrontMatter(raw)
	if err != nil {
		return nil, fmt.Errorf("%s/lesson.md: %w", dir, err)
	}
	l := &Lesson{Dir: dir, Body: body}
	if err := yaml.Unmarshal(front, l); err != nil {
		return nil, fmt.Errorf("%s/lesson.md front matter: %w", dir, err)
	}
	if l.Title == "" {
		return nil, fmt.Errorf("%s/lesson.md: title is required", dir)
	}
	for _, f := range l.Files {
		if f == "" || filepath.IsAbs(f) || strings.Contains(filepath.ToSlash(f), "..") {
			return nil, fmt.Errorf("%s/lesson.md: bad file name %q", dir, f)
		}
	}
	if entries, err := os.ReadDir(l.TestsDir()); err == nil && len(entries) > 0 {
		l.HasTest = true
	}
	return l, nil
}

func splitFrontMatter(raw []byte) (front []byte, body string, err error) {
	raw = bytes.TrimPrefix(raw, []byte("\xef\xbb\xbf"))
	raw = bytes.ReplaceAll(raw, []byte("\r\n"), []byte("\n"))
	if !bytes.HasPrefix(raw, []byte("---\n")) {
		return nil, "", fmt.Errorf("missing front matter")
	}
	rest := raw[4:]
	end := bytes.Index(rest, []byte("\n---\n"))
	if end < 0 {
		return nil, "", fmt.Errorf("unterminated front matter")
	}
	return rest[:end], string(rest[end+5:]), nil
}
