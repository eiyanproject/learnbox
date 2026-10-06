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
	Lang        string `yaml:"-" json:"lang"`
	Title       string `yaml:"title" json:"title"`
	Description string `yaml:"description" json:"description"`
	Order       int    `yaml:"order" json:"-"`
	// Badge names the badge for finishing every guided lesson in the track.
	Badge string `yaml:"badge" json:"-"`
	// Group "misc" lists the track in the Misc area, apart from the
	// programming tracks.
	Group    string    `yaml:"group" json:"group,omitempty"`
	Sections []Section `yaml:"sections" json:"sections"`
}

type Section struct {
	ID          string `yaml:"id" json:"id"`
	Title       string `yaml:"title" json:"title"`
	Description string `yaml:"description" json:"description"`
	// Arena marks the track's challenge ladder. Its lessons are timed
	// challenges, listed on the Arena page rather than in the track.
	Arena bool `yaml:"arena" json:"arena,omitempty"`
	// XP is what each lesson in the section is worth before hint costs; see
	// internal/game for the default and for how rated practice exercises differ.
	XP int `yaml:"xp" json:"xp,omitempty"`
	// Beginner marks the track's entry-level section, for the badges about
	// leaving it behind.
	Beginner bool      `yaml:"beginner" json:"-"`
	Lessons  []*Lesson `yaml:"-" json:"lessons"`
}

// Challenge is the front matter of an arena lesson.
type Challenge struct {
	Boss bool `yaml:"boss" json:"boss"`
	// Minutes is the time limit; CooldownMinutes the wait after a loss.
	Minutes         int `yaml:"minutes" json:"minutes"`
	CooldownMinutes int `yaml:"cooldown_minutes" json:"cooldown_minutes"`
	// XP is the reward for a win before the speed bonus.
	XP       int      `yaml:"xp" json:"xp"`
	Requires Requires `yaml:"requires" json:"requires"`
}

// Requires gates a challenge. Every earlier challenge in the same ladder must
// also have been won; that rule is implied, not written here.
type Requires struct {
	XP     int      `yaml:"xp" json:"xp,omitempty"`         // XP earned in this track
	Badges []string `yaml:"badges" json:"badges,omitempty"` // badge ids
}

type Lesson struct {
	Lang    string `yaml:"-" json:"lang"`
	Section string `yaml:"-" json:"section"`
	Slug    string `yaml:"-" json:"slug"`

	Title      string `yaml:"title" json:"title"`
	Summary    string `yaml:"summary" json:"summary"`
	Order      int    `yaml:"order" json:"-"`
	Difficulty int    `yaml:"difficulty" json:"difficulty,omitempty"`
	// Kind "quiz" is a set of questions (questions.yaml, see internal/quiz)
	// instead of code with tests.
	Kind   string   `yaml:"kind" json:"kind,omitempty"`
	Files  []string `yaml:"files" json:"files"`
	Run    string   `yaml:"run" json:"run,omitempty"`
	Hints  []string `yaml:"hints" json:"-"`
	Source string   `yaml:"source" json:"source,omitempty"` // attribution, Markdown
	// Challenge is set for lessons in an arena section.
	Challenge *Challenge `yaml:"challenge" json:"challenge,omitempty"`

	Dir  string `yaml:"-" json:"-"`
	Body string `yaml:"-" json:"-"` // Markdown
	// BodyLine is the line of lesson.md the body starts on, so anything
	// found in Body can be reported at its real line in the file.
	BodyLine int  `yaml:"-" json:"-"`
	HasTest  bool `yaml:"-" json:"has_tests"`
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

// Neighbours returns the lessons before and after id. They run on across
// sections in track order, so the last Beginner lesson leads into
// Intermediate.
func (lib *Library) Neighbours(id string) (prev, next *Lesson) {
	l := lib.lessons[id]
	if l == nil {
		return nil, nil
	}
	for _, t := range lib.Tracks {
		if t.Lang != l.Lang {
			continue
		}
		var all []*Lesson
		for _, s := range t.Sections {
			// Arena challenges are not a next lesson to wander into: they
			// are entered from the Arena, with a clock.
			if s.Arena != (l.Challenge != nil) {
				continue
			}
			all = append(all, s.Lessons...)
		}
		for i, x := range all {
			if x == l {
				if i > 0 {
					prev = all[i-1]
				}
				if i+1 < len(all) {
					next = all[i+1]
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
					if err := checkChallenge(l, sec.Arena); err != nil {
						return nil, err
					}
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
	// "---" is line 1, the front matter follows, then the closing "---"; the
	// body begins on the line after that.
	l := &Lesson{Dir: dir, Body: body, BodyLine: bytes.Count(front, []byte("\n")) + 4}
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

// checkChallenge applies defaults to an arena lesson's challenge settings and
// refuses a challenge outside an arena, or an arena lesson without one.
func checkChallenge(l *Lesson, arena bool) error {
	c := l.Challenge
	switch {
	case arena && c == nil:
		return fmt.Errorf("%s: lessons in an arena section need a challenge: block", l.ID())
	case !arena && c != nil:
		return fmt.Errorf("%s: challenge: is only allowed in an arena section", l.ID())
	case c == nil:
		return nil
	}
	if c.Minutes <= 0 {
		return fmt.Errorf("%s: challenge.minutes must be positive", l.ID())
	}
	if c.CooldownMinutes <= 0 {
		c.CooldownMinutes = 3
		if c.Boss {
			c.CooldownMinutes = 5
		}
	}
	if c.XP <= 0 {
		c.XP = 150
		if c.Boss {
			c.XP = 500
		}
	}
	if !l.HasTest {
		return fmt.Errorf("%s: a challenge needs tests to be won", l.ID())
	}
	return nil
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
