package quiz

import (
	"math/rand/v2"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
)

// lib builds a one-track library with the given topics' questions.yaml.
func lib(t *testing.T, topics map[string]string) *content.Library {
	t.Helper()
	root := t.TempDir()
	track := filepath.Join(root, "drive")
	must := func(err error) {
		if err != nil {
			t.Fatal(err)
		}
	}
	must(os.MkdirAll(track, 0o755))
	must(os.WriteFile(filepath.Join(track, "track.yaml"), []byte("title: Drive\ngroup: misc\nsections:\n  - id: rules\n    title: Rules\n"), 0o644))
	i := 0
	for slug, yml := range topics {
		i++
		dir := filepath.Join(track, "rules", slug)
		must(os.MkdirAll(dir, 0o755))
		md := "---\ntitle: " + slug + "\nkind: quiz\norder: " + string(rune('0'+i)) + "\n---\nNotes.\n"
		must(os.WriteFile(filepath.Join(dir, "lesson.md"), []byte(md), 0o644))
		must(os.WriteFile(filepath.Join(dir, "questions.yaml"), []byte(yml), 0o644))
	}
	l, err := content.Load(root)
	if err != nil {
		t.Fatal(err)
	}
	return l
}

func tf(id string, answer bool, exams string) string {
	a := "false"
	if answer {
		a = "true"
	}
	return "- id: " + id + "\n  en: E\n  ja: J\n  answer: " + a + "\n  why: W\n  ref: R\n  exams: [" + exams + "]\n"
}

const scenario = `- id: sc-1
  kind: scenario
  en: Scene
  ja: 場面
  ref: R
  exams: [hon]
  statements:
    - {en: a, ja: a, answer: true, why: w}
    - {en: b, ja: b, answer: false, why: w}
    - {en: c, ja: c, answer: true, why: w}
`

func TestLoadAndMark(t *testing.T) {
	banks, err := Load(lib(t, map[string]string{"signals": tf("q1", true, "kari, hon") + tf("q2", false, "hon") + scenario}))
	if err != nil {
		t.Fatal(err)
	}
	b := banks["drive"]
	if b == nil || len(b.Questions) != 3 {
		t.Fatalf("got %+v", b)
	}
	yes, no := true, false
	if !Mark(b.Question("q1"), Given{Answer: &yes}) || Mark(b.Question("q1"), Given{Answer: &no}) {
		t.Error("true/false marking")
	}
	if Mark(b.Question("q1"), Given{}) {
		t.Error("an unanswered question must be wrong")
	}
	sc := b.Question("sc-1")
	if !Mark(sc, Given{Answers: []bool{true, false, true}}) {
		t.Error("all three right should score")
	}
	if Mark(sc, Given{Answers: []bool{true, true, true}}) || Mark(sc, Given{Answers: []bool{true, false}}) {
		t.Error("a scenario scores only when all three are right")
	}
	if b.Question("q1").Topic != "drive/rules/signals" {
		t.Errorf("topic: %q", b.Question("q1").Topic)
	}
}

func TestBrokenBanksAreRefused(t *testing.T) {
	cases := map[string]string{
		"no answer":       "- {id: a, en: E, ja: J, why: W, ref: R, exams: [hon]}\n",
		"no japanese":     "- {id: a, en: E, answer: true, why: W, ref: R, exams: [hon]}\n",
		"no ref":          "- {id: a, en: E, ja: J, answer: true, why: W, exams: [hon]}\n",
		"bad exam":        "- {id: a, en: E, ja: J, answer: true, why: W, ref: R, exams: [menkyo]}\n",
		"bad id":          "- {id: A_1, en: E, ja: J, answer: true, why: W, ref: R, exams: [hon]}\n",
		"duplicate":       tf("a", true, "hon") + tf("a", false, "hon"),
		"scenario kari":   strings.Replace(scenario, "exams: [hon]", "exams: [kari]", 1),
		"image not https": "- {id: a, en: E, ja: J, answer: true, why: W, ref: R, exams: [hon], image: 'http://example.org/a.svg'}\n",
		"image no host":   "- {id: a, en: E, ja: J, answer: true, why: W, ref: R, exams: [hon], image: 'sign.svg'}\n",
		"two statements":  strings.Replace(scenario, "    - {en: c, ja: c, answer: true, why: w}\n", "", 1),
	}
	for name, yml := range cases {
		if _, err := Load(lib(t, map[string]string{"t": yml})); err == nil {
			t.Errorf("%s: accepted", name)
		}
	}
}

func TestDrawFollowsTheSpec(t *testing.T) {
	var yml strings.Builder
	for i := range 60 {
		yml.WriteString(tf("q"+string(rune('a'+i/26))+string(rune('a'+i%26)), i%2 == 0, "kari, hon"))
	}
	banks, err := Load(lib(t, map[string]string{"t": yml.String()}))
	if err != nil {
		t.Fatal(err)
	}
	b := banks["drive"]
	qs, err := b.Draw(Specs["kari"], rand.New(rand.NewPCG(1, 2)))
	if err != nil {
		t.Fatal(err)
	}
	seen := map[string]bool{}
	for _, q := range qs {
		if seen[q.ID] {
			t.Fatalf("drew %s twice", q.ID)
		}
		seen[q.ID] = true
	}
	if len(qs) != 50 {
		t.Fatalf("drew %d", len(qs))
	}
	if _, err := b.Draw(Specs["hon"], rand.New(rand.NewPCG(1, 2))); err == nil {
		t.Fatal("hon needs 90 + 5 scenarios; 60 should not be enough")
	}
}

func TestSpecsAddUpToAHundred(t *testing.T) {
	for id, s := range Specs {
		if got := s.TF*s.TFPoints + s.Scenarios*s.ScPoints; got != s.Max || s.Max != 100 || s.Pass != 90 {
			t.Errorf("%s: %d points, max %d, pass %d", id, got, s.Max, s.Pass)
		}
	}
}

func TestMistakesClearAfterTwoRightInARow(t *testing.T) {
	s, err := Open(filepath.Join(t.TempDir(), "quiz.json"))
	if err != nil {
		t.Fatal(err)
	}
	now := time.Now()
	s.Answered("drive", map[string]bool{"q1": false}, now)
	if !s.Records("drive")["q1"].Mistake() {
		t.Fatal("a wrong answer should be a mistake")
	}
	s.Answered("drive", map[string]bool{"q1": true}, now)
	if !s.Records("drive")["q1"].Mistake() {
		t.Fatal("one right answer is not enough")
	}
	s.Answered("drive", map[string]bool{"q1": true}, now)
	if s.Records("drive")["q1"].Mistake() {
		t.Fatal("two in a row should clear it")
	}
	if len(s.Records("other")) != 0 {
		t.Fatal("records leak between tracks")
	}
}

func TestExamLifecycleSurvivesReopen(t *testing.T) {
	path := filepath.Join(t.TempDir(), "quiz.json")
	s, _ := Open(path)
	now := time.Now().UTC().Truncate(time.Second)
	s.Start("drive", Active{Exam: "kari", IDs: []string{"q1"}, Started: now, Deadline: now.Add(30 * time.Minute)})

	s2, err := Open(path)
	if err != nil {
		t.Fatal(err)
	}
	a, ok := s2.Active("drive", "kari")
	if !ok || !a.Deadline.Equal(now.Add(30*time.Minute)) {
		t.Fatalf("active exam lost: %+v", a)
	}
	s2.Finish(Result{Track: "drive", Exam: "kari", At: now, Score: 92, Max: 100, Passed: true}, map[string]bool{"q1": false})
	if _, ok := s2.Active("drive", "kari"); ok {
		t.Fatal("still active after finishing")
	}
	if r := s2.Results("drive"); len(r) != 1 || r[0].Score != 92 {
		t.Fatalf("results: %+v", r)
	}
	if !s2.Records("drive")["q1"].Mistake() {
		t.Fatal("an exam's wrong answers should feed the mistakes review")
	}
}
