// Package quiz runs true/false question banks: studying them by topic, timed
// mock exams in a real exam's format, and a review of what was got wrong.
//
// A quiz track is an ordinary track whose lessons have `kind: quiz` and a
// questions.yaml beside lesson.md. lesson.md holds the topic's study notes;
// questions.yaml holds the questions:
//
//   - id: sig-red-arrow          # unique within the track
//     en: "..."                  # the statement, in English
//     ja: "..."                  # and in Japanese
//     answer: false              # true is ○, false is ×
//     why: "..."                 # the rule behind the answer
//     ref: "教則 第5章第3節2"     # where the rule is written
//     exams: [kari, hon]         # which mock exams may draw it
//
// A scenario question - the illustration questions of the full licence test -
// has `kind: scenario`, a scene in en/ja, and exactly three statements, each
// with its own en, ja, answer and why. It scores only if all three are right.
package quiz

import (
	"fmt"
	"math/rand/v2"
	"os"
	"path/filepath"
	"regexp"
	"slices"

	"gopkg.in/yaml.v3"

	"github.com/eiyanproject/learnbox/internal/content"
)

type Statement struct {
	EN     string `yaml:"en" json:"en"`
	JA     string `yaml:"ja" json:"ja"`
	Answer *bool  `yaml:"answer" json:"-"`
	Why    string `yaml:"why" json:"-"`
}

type Question struct {
	ID         string      `yaml:"id" json:"id"`
	Kind       string      `yaml:"kind" json:"kind,omitempty"` // "" or "scenario"
	EN         string      `yaml:"en" json:"en"`
	JA         string      `yaml:"ja" json:"ja"`
	Answer     *bool       `yaml:"answer" json:"-"`
	Why        string      `yaml:"why" json:"-"`
	Ref        string      `yaml:"ref" json:"-"`
	Exams      []string    `yaml:"exams" json:"-"`
	Statements []Statement `yaml:"statements" json:"statements,omitempty"`

	Topic string `yaml:"-" json:"topic"` // the lesson id it belongs to
}

func (q *Question) Scenario() bool { return q.Kind == "scenario" }

// Spec is an exam's format.
type Spec struct {
	ID        string `json:"id"`
	Title     string `json:"title"`
	TF        int    `json:"tf"`        // true/false questions drawn
	Scenarios int    `json:"scenarios"` // scenario questions drawn
	Minutes   int    `json:"minutes"`
	TFPoints  int    `json:"tf_points"`
	ScPoints  int    `json:"scenario_points"`
	Pass      int    `json:"pass"`
	Max       int    `json:"max"`
}

// Specs are the two written tests for a Japanese ordinary licence.
// 仮免: 50 true/false at 2 points, 30 minutes. 本免: 90 true/false at 1 point
// and 5 illustration questions at 2 points, 50 minutes. Both pass at 90/100.
var Specs = map[string]Spec{
	"kari": {ID: "kari", Title: "Provisional licence (仮免)", TF: 50, Minutes: 30, TFPoints: 2, Pass: 90, Max: 100},
	"hon":  {ID: "hon", Title: "Full licence (本免)", TF: 90, Scenarios: 5, Minutes: 50, TFPoints: 1, ScPoints: 2, Pass: 90, Max: 100},
}

// SpecOrder is the order exams are listed in.
var SpecOrder = []string{"kari", "hon"}

// Bank is one quiz track's questions.
type Bank struct {
	Track     string
	Questions []*Question // in topic order, then file order
	byID      map[string]*Question
	byTopic   map[string][]*Question
}

func (b *Bank) Question(id string) *Question { return b.byID[id] }

func (b *Bank) Topic(lessonID string) []*Question { return b.byTopic[lessonID] }

// Pool lists the questions an exam may draw, split by kind.
func (b *Bank) Pool(exam string) (tf, scenarios []*Question) {
	for _, q := range b.Questions {
		if !slices.Contains(q.Exams, exam) {
			continue
		}
		if q.Scenario() {
			scenarios = append(scenarios, q)
		} else {
			tf = append(tf, q)
		}
	}
	return tf, scenarios
}

// Draw picks an exam's questions at random: the true/false ones first, then
// the scenarios, as the real test lays them out.
func (b *Bank) Draw(spec Spec, r *rand.Rand) ([]*Question, error) {
	tf, sc := b.Pool(spec.ID)
	if len(tf) < spec.TF || len(sc) < spec.Scenarios {
		return nil, fmt.Errorf("%s needs %d true/false and %d scenario questions; the bank has %d and %d",
			spec.ID, spec.TF, spec.Scenarios, len(tf), len(sc))
	}
	pick := func(from []*Question, n int) []*Question {
		idx := r.Perm(len(from))[:n]
		out := make([]*Question, n)
		for i, j := range idx {
			out[i] = from[j]
		}
		return out
	}
	return append(pick(tf, spec.TF), pick(sc, spec.Scenarios)...), nil
}

// Given is an answer to one question: Answer for true/false, Answers (three
// of them) for a scenario.
type Given struct {
	Answer  *bool  `json:"answer,omitempty"`
	Answers []bool `json:"answers,omitempty"`
}

// Mark reports whether g answers q correctly. An unanswered question is wrong.
func Mark(q *Question, g Given) bool {
	if q.Scenario() {
		if len(g.Answers) != len(q.Statements) {
			return false
		}
		for i, s := range q.Statements {
			if g.Answers[i] != *s.Answer {
				return false
			}
		}
		return true
	}
	return g.Answer != nil && *g.Answer == *q.Answer
}

// Points is what a correct answer to q is worth in spec.
func Points(spec Spec, q *Question) int {
	if q.Scenario() {
		return spec.ScPoints
	}
	return spec.TFPoints
}

var validID = regexp.MustCompile(`^[a-z0-9][a-z0-9-]{0,47}$`)

// Load reads the questions of every quiz lesson in lib, one bank per track,
// and checks them. A broken bank stops the load: a question with no answer,
// or a duplicate id, is a content bug to fix, not to serve.
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
					b = &Bank{Track: t.Lang, byID: map[string]*Question{}, byTopic: map[string][]*Question{}}
					banks[t.Lang] = b
				}
				if err := b.add(l); err != nil {
					return nil, err
				}
			}
		}
	}
	return banks, nil
}

func (b *Bank) add(l *content.Lesson) error {
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
		if err := check(q); err != nil {
			return fmt.Errorf("%s/questions.yaml: %w", l.ID(), err)
		}
		if _, dup := b.byID[q.ID]; dup {
			return fmt.Errorf("%s/questions.yaml: question id %q is used twice in this track", l.ID(), q.ID)
		}
		q.Topic = l.ID()
		b.byID[q.ID] = q
		b.byTopic[l.ID()] = append(b.byTopic[l.ID()], q)
		b.Questions = append(b.Questions, q)
	}
	return nil
}

func check(q *Question) error {
	where := fmt.Sprintf("question %q", q.ID)
	switch {
	case !validID.MatchString(q.ID):
		return fmt.Errorf("%s: id must be lower-case letters, digits and dashes", where)
	case q.EN == "" || q.JA == "":
		return fmt.Errorf("%s: needs both en and ja", where)
	case q.Ref == "":
		return fmt.Errorf("%s: needs a ref to the rule it rests on", where)
	case len(q.Exams) == 0:
		return fmt.Errorf("%s: needs exams (kari, hon or both)", where)
	}
	for _, e := range q.Exams {
		if _, ok := Specs[e]; !ok {
			return fmt.Errorf("%s: unknown exam %q", where, e)
		}
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
		if !slices.Equal(q.Exams, []string{"hon"}) {
			return fmt.Errorf("%s: scenario questions are only in the full licence test (exams: [hon])", where)
		}
		for i, s := range q.Statements {
			if s.EN == "" || s.JA == "" || s.Answer == nil || s.Why == "" {
				return fmt.Errorf("%s: statement %d needs en, ja, answer and why", where, i+1)
			}
		}
	default:
		return fmt.Errorf("%s: unknown kind %q", where, q.Kind)
	}
	return nil
}
