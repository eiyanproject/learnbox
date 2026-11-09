// Package quiz runs question banks: studying them by topic, timed mock exams
// in a real exam's format, and a review of what was got wrong.
//
// A quiz track is an ordinary track whose lessons have `kind: quiz` and a
// questions.yaml beside lesson.md. lesson.md holds the topic's study notes;
// questions.yaml holds the questions. A true/false question:
//
//   - id: sig-red-arrow          # unique within the track
//     en: "..."                  # the statement, in English
//     ja: "..."                  # and in Japanese (required if the track is bilingual)
//     answer: false              # true is ○, false is ×
//     why: "..."                 # the rule behind the answer
//     ref: "教則 第5章第3節2"     # where the rule is written
//     exams: [kari, hon]         # which mock exams may draw it
//     image: "https://..."       # optional: a picture shown with the question
//
// A scenario question - the illustration questions of the full licence test -
// has `kind: scenario`, a scene in en/ja, and exactly three statements, each
// with its own en, ja, answer and why. It scores only if all three are right.
//
// A multiple-choice question has `kind: choice`, `options` (lettered A, B, ...
// in the order written) and `correct`: one letter, or several for a "choose
// two" question, which scores only if exactly those are picked.
//
// Any question may carry a `scene`: a diagram of it, described in scene.go.
// The mock exams themselves are declared in the track's track.yaml.
package quiz

import (
	"fmt"
	"math/rand/v2"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"slices"
	"strings"

	"gopkg.in/yaml.v3"

	"github.com/eiyanproject/learnbox/internal/content"
)

type Statement struct {
	EN     string `yaml:"en" json:"en"`
	JA     string `yaml:"ja" json:"ja,omitempty"`
	Answer *bool  `yaml:"answer" json:"-"`
	Why    string `yaml:"why" json:"-"`
}

type Question struct {
	ID     string `yaml:"id" json:"id"`
	Kind   string `yaml:"kind" json:"kind,omitempty"` // "", "scenario" or "choice"
	EN     string `yaml:"en" json:"en"`
	JA     string `yaml:"ja" json:"ja,omitempty"`
	Answer *bool  `yaml:"answer" json:"-"`
	Why    string `yaml:"why" json:"-"`
	Ref    string `yaml:"ref" json:"-"`
	// Image is the address of a picture shown with the question - a road sign,
	// say. It is linked, never copied: the browser fetches it, so a question
	// must still make sense when the picture does not load.
	Image      string      `yaml:"image" json:"image,omitempty"`
	Exams      []string    `yaml:"exams" json:"-"`
	Statements []Statement `yaml:"statements" json:"statements,omitempty"`
	// Options and Correct make a multiple-choice question. Choose is how many
	// to pick: the real exam says "choose two", so the learner may know it.
	Options []string `yaml:"options" json:"options,omitempty"`
	Correct []string `yaml:"correct" json:"-"`
	Choose  int      `yaml:"-" json:"choose,omitempty"`
	// Scene is a diagram of the question's situation, drawn by the browser.
	Scene *Scene `yaml:"scene" json:"scene,omitempty"`

	Topic string `yaml:"-" json:"topic"` // the lesson id it belongs to
}

func (q *Question) Scenario() bool { return q.Kind == "scenario" }

// kind is the question's kind as an exam part names it.
func (q *Question) kind() string {
	if q.Kind == "" {
		return "tf"
	}
	return q.Kind
}

// CorrectPicks is Correct as option indexes, A = 0, in order.
func (q *Question) CorrectPicks() []int {
	out := make([]int, 0, len(q.Correct))
	for _, c := range q.Correct {
		out = append(out, int(c[0]-'A'))
	}
	slices.Sort(out)
	return out
}

// Spec is a mock exam's format, as its track declares it.
type Spec = content.Exam

// Bank is one quiz track's questions and mock exams.
type Bank struct {
	Track     string
	Exams     []Spec
	Questions []*Question // in topic order, then file order
	byID      map[string]*Question
	byTopic   map[string][]*Question
}

func (b *Bank) Question(id string) *Question { return b.byID[id] }

func (b *Bank) Topic(lessonID string) []*Question { return b.byTopic[lessonID] }

// Exam finds one of the track's mock exams.
func (b *Bank) Exam(id string) (Spec, bool) {
	for _, e := range b.Exams {
		if e.ID == id {
			return e, true
		}
	}
	return Spec{}, false
}

// Pool lists the questions one part of an exam may draw from.
func (b *Bank) Pool(exam string, part content.ExamPart) []*Question {
	var out []*Question
	for _, q := range b.Questions {
		if slices.Contains(q.Exams, exam) && q.kind() == part.Kind && strings.HasPrefix(q.Topic, part.From) {
			out = append(out, q)
		}
	}
	return out
}

// Shortfalls describes each part of spec the bank cannot fill; none means an
// exam can be drawn. Parts are filled in order and never share a question.
func (b *Bank) Shortfalls(spec Spec) []string {
	var out []string
	used := map[string]bool{}
	for _, part := range spec.Draw {
		free := 0
		for _, q := range b.Pool(spec.ID, part) {
			if !used[q.ID] {
				free++
				if free <= part.Count {
					used[q.ID] = true
				}
			}
		}
		if free < part.Count {
			out = append(out, fmt.Sprintf("%s%s %d of %d", part.Kind, fromNote(part), free, part.Count))
		}
	}
	return out
}

func fromNote(p content.ExamPart) string {
	if p.From == "" {
		return ""
	}
	return " from " + p.From
}

// Draw picks an exam's questions at random, part by part - true/false first
// and then the scenarios for the driving test, as the real one lays them out -
// or mixed together if the exam says shuffle.
func (b *Bank) Draw(spec Spec, r *rand.Rand) ([]*Question, error) {
	if short := b.Shortfalls(spec); len(short) > 0 {
		return nil, fmt.Errorf("%s cannot be drawn yet: has %s", spec.ID, strings.Join(short, ", "))
	}
	used := map[string]bool{}
	var out []*Question
	for _, part := range spec.Draw {
		var free []*Question
		for _, q := range b.Pool(spec.ID, part) {
			if !used[q.ID] {
				free = append(free, q)
			}
		}
		for _, i := range r.Perm(len(free))[:part.Count] {
			used[free[i].ID] = true
			out = append(out, free[i])
		}
	}
	if spec.Shuffle {
		r.Shuffle(len(out), func(i, j int) { out[i], out[j] = out[j], out[i] })
	}
	return out, nil
}

// Given is an answer to one question: Answer for true/false, Answers (three
// of them) for a scenario, Picks (option indexes, A = 0) for multiple choice.
type Given struct {
	Answer  *bool  `json:"answer,omitempty"`
	Answers []bool `json:"answers,omitempty"`
	Picks   []int  `json:"picks,omitempty"`
}

// Mark reports whether g answers q correctly. An unanswered question is wrong.
func Mark(q *Question, g Given) bool {
	switch q.Kind {
	case "scenario":
		if len(g.Answers) != len(q.Statements) {
			return false
		}
		for i, s := range q.Statements {
			if g.Answers[i] != *s.Answer {
				return false
			}
		}
		return true
	case "choice":
		picks := slices.Clone(g.Picks)
		slices.Sort(picks)
		return slices.Equal(slices.Compact(picks), q.CorrectPicks())
	}
	return g.Answer != nil && *g.Answer == *q.Answer
}

// Points is what a correct answer to q is worth in spec: the points of the
// first part that could have drawn it.
func Points(spec Spec, q *Question) int {
	for _, part := range spec.Draw {
		if part.Kind == q.kind() && strings.HasPrefix(q.Topic, part.From) {
			return part.Points
		}
	}
	return 0
}

// Possible is the most points spec can give.
func Possible(spec Spec) int {
	n := 0
	for _, part := range spec.Draw {
		n += part.Count * part.Points
	}
	return n
}

// Scale turns points earned into the exam's reported score, out of spec.Max,
// rounded to the nearest whole point. For the driving tests the points already
// add up to 100, so the score is the points.
func Scale(spec Spec, earned int) int {
	possible := Possible(spec)
	if possible == 0 {
		return 0
	}
	return (earned*spec.Max + possible/2) / possible
}

var (
	validID   = regexp.MustCompile(`^[a-z0-9][a-z0-9-]{0,47}$`)
	partKinds = []string{"tf", "scenario", "choice"}
)

// Load reads the questions of every quiz lesson in lib, one bank per track,
// and checks them and the track's exams. A broken bank stops the load: a
// question with no answer, or a duplicate id, is a content bug to fix, not to
// serve.
func Load(lib *content.Library) (map[string]*Bank, error) {
	banks := map[string]*Bank{}
	for _, t := range lib.Tracks {
		for _, s := range t.Sections {
			for _, l := range s.Lessons {
				if l.Kind != "quiz" {
					continue
				}
				b := banks[t.Lang]
				if b == nil {
					if err := checkExams(t); err != nil {
						return nil, err
					}
					b = &Bank{Track: t.Lang, Exams: t.Exams, byID: map[string]*Question{}, byTopic: map[string][]*Question{}}
					banks[t.Lang] = b
				}
				if err := b.add(l, t.Bilingual); err != nil {
					return nil, err
				}
			}
		}
	}
	return banks, nil
}

func checkExams(t *content.Track) error {
	seen := map[string]bool{}
	for _, e := range t.Exams {
		where := fmt.Sprintf("%s/track.yaml: exam %q", t.Lang, e.ID)
		switch {
		case !validID.MatchString(e.ID) || seen[e.ID]:
			return fmt.Errorf("%s: id must be unique lower-case letters, digits and dashes", where)
		case e.Title == "" || e.Minutes <= 0 || e.Max <= 0:
			return fmt.Errorf("%s: needs a title, minutes and max", where)
		case e.Pass <= 0 || e.Pass > e.Max:
			return fmt.Errorf("%s: pass must be between 1 and max", where)
		case len(e.Draw) == 0:
			return fmt.Errorf("%s: draws nothing", where)
		}
		seen[e.ID] = true
		for _, p := range e.Draw {
			if !slices.Contains(partKinds, p.Kind) || p.Count <= 0 || p.Points <= 0 {
				return fmt.Errorf("%s: each draw needs a kind (tf, scenario or choice), a count and points", where)
			}
		}
	}
	return nil
}

func (b *Bank) add(l *content.Lesson, bilingual bool) error {
	path := filepath.Join(l.Dir, "questions.yaml")
	raw, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("%s: a quiz lesson needs questions.yaml: %w", l.ID(), err)
	}
	var qs []*Question
	if err := yaml.Unmarshal(raw, &qs); err != nil {
		return fmt.Errorf("%s/questions.yaml: %w", l.ID(), err)
	}
	if len(qs) == 0 {
		return fmt.Errorf("%s/questions.yaml: no questions", l.ID())
	}
	for _, q := range qs {
		if err := b.check(q, bilingual); err != nil {
			return fmt.Errorf("%s/questions.yaml: %w", l.ID(), err)
		}
		if _, dup := b.byID[q.ID]; dup {
			return fmt.Errorf("%s/questions.yaml: question id %q is used twice in this track", l.ID(), q.ID)
		}
		q.Topic = l.ID()
		if q.Kind == "choice" {
			q.Choose = len(q.Correct)
		}
		b.byID[q.ID] = q
		b.byTopic[l.ID()] = append(b.byTopic[l.ID()], q)
		b.Questions = append(b.Questions, q)
	}
	return nil
}

func (b *Bank) check(q *Question, bilingual bool) error {
	where := fmt.Sprintf("question %q", q.ID)
	switch {
	case !validID.MatchString(q.ID):
		return fmt.Errorf("%s: id must be lower-case letters, digits and dashes", where)
	case q.EN == "":
		return fmt.Errorf("%s: needs en", where)
	case bilingual && q.JA == "":
		return fmt.Errorf("%s: this track is bilingual; needs ja as well as en", where)
	case q.Ref == "":
		return fmt.Errorf("%s: needs a ref to the rule it rests on", where)
	case len(q.Exams) == 0:
		return fmt.Errorf("%s: needs exams: the mock exams that may draw it", where)
	}
	for _, e := range q.Exams {
		if _, ok := b.Exam(e); !ok {
			return fmt.Errorf("%s: exam %q is not declared in track.yaml", where, e)
		}
	}
	if q.Scene != nil {
		if err := q.Scene.check(); err != nil {
			return fmt.Errorf("%s: %w", where, err)
		}
	}
	if q.Image != "" {
		u, err := url.Parse(q.Image)
		if err != nil || u.Scheme != "https" || u.Host == "" {
			return fmt.Errorf("%s: image must be an https address", where)
		}
	}
	if q.Kind != "choice" && (len(q.Options) > 0 || len(q.Correct) > 0) {
		return fmt.Errorf("%s: options and correct belong to a choice question", where)
	}
	switch q.Kind {
	case "":
		if q.Answer == nil || q.Why == "" {
			return fmt.Errorf("%s: a true/false question needs answer and why", where)
		}
		if len(q.Statements) > 0 {
			return fmt.Errorf("%s: statements belong to a scenario question", where)
		}
	case "scenario":
		if len(q.Statements) != 3 {
			return fmt.Errorf("%s: a scenario has exactly 3 statements", where)
		}
		if q.Answer != nil {
			return fmt.Errorf("%s: a scenario's answers go on its statements", where)
		}
		for i, s := range q.Statements {
			if s.EN == "" || (bilingual && s.JA == "") || s.Answer == nil || s.Why == "" {
				return fmt.Errorf("%s: statement %d needs en, answer and why (and ja in a bilingual track)", where, i+1)
			}
		}
	case "choice":
		if q.Answer != nil || len(q.Statements) > 0 {
			return fmt.Errorf("%s: a choice question has options and correct, not answer or statements", where)
		}
		if len(q.Options) < 3 || len(q.Options) > 8 {
			return fmt.Errorf("%s: a choice question has 3 to 8 options", where)
		}
		for i, o := range q.Options {
			if strings.TrimSpace(o) == "" {
				return fmt.Errorf("%s: option %c is empty", where, 'A'+i)
			}
		}
		if len(q.Correct) == 0 || len(q.Correct) >= len(q.Options) {
			return fmt.Errorf("%s: correct names at least one option, and not all of them", where)
		}
		seen := map[string]bool{}
		for _, c := range q.Correct {
			if len(c) != 1 || c[0] < 'A' || int(c[0]-'A') >= len(q.Options) || seen[c] {
				return fmt.Errorf("%s: correct %q is not one of the options A to %c", where, c, 'A'+len(q.Options)-1)
			}
			seen[c] = true
		}
		if q.Why == "" {
			return fmt.Errorf("%s: a choice question needs why", where)
		}
	default:
		return fmt.Errorf("%s: unknown kind %q", where, q.Kind)
	}
	return nil
}
