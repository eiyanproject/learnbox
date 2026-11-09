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

// driveTrack is a bilingual quiz track with the two driving tests and a small
// multiple-choice exam scored out of 1,000.
const driveTrack = `title: Drive
group: misc
bilingual: true
exams:
  - {id: kari, title: K, minutes: 30, pass: 90, max: 100, draw: [{kind: tf, count: 50, points: 2}]}
  - id: hon
    title: H
    minutes: 50
    pass: 90
    max: 100
    draw: [{kind: tf, count: 90, points: 1}, {kind: scenario, count: 5, points: 2}]
  - {id: mc, title: M, minutes: 10, pass: 720, max: 1000, shuffle: true, draw: [{kind: choice, count: 3, points: 1}]}
sections:
  - id: rules
    title: Rules
`

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
	must(os.WriteFile(filepath.Join(track, "track.yaml"), []byte(driveTrack), 0o644))
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
		"no answer":         "- {id: a, en: E, ja: J, why: W, ref: R, exams: [hon]}\n",
		"no japanese":       "- {id: a, en: E, answer: true, why: W, ref: R, exams: [hon]}\n",
		"no ref":            "- {id: a, en: E, ja: J, answer: true, why: W, exams: [hon]}\n",
		"bad exam":          "- {id: a, en: E, ja: J, answer: true, why: W, ref: R, exams: [menkyo]}\n",
		"bad id":            "- {id: A_1, en: E, ja: J, answer: true, why: W, ref: R, exams: [hon]}\n",
		"duplicate":         tf("a", true, "hon") + tf("a", false, "hon"),
		"choice no options": "- {id: a, kind: choice, en: E, ja: J, why: W, ref: R, exams: [mc], correct: [A]}\n",
		"choice bad letter": "- {id: a, kind: choice, en: E, ja: J, why: W, ref: R, exams: [mc], options: [x, y, z], correct: [D]}\n",
		"choice all right":  "- {id: a, kind: choice, en: E, ja: J, why: W, ref: R, exams: [mc], options: [x, y, z], correct: [A, B, C]}\n",
		"choice no why":     "- {id: a, kind: choice, en: E, ja: J, ref: R, exams: [mc], options: [x, y, z], correct: [A]}\n",
		"options on tf":     "- {id: a, en: E, ja: J, answer: true, why: W, ref: R, exams: [hon], options: [x, y, z]}\n",
		"image not https":   "- {id: a, en: E, ja: J, answer: true, why: W, ref: R, exams: [hon], image: 'http://example.org/a.svg'}\n",
		"image no host":     "- {id: a, en: E, ja: J, answer: true, why: W, ref: R, exams: [hon], image: 'sign.svg'}\n",
		"two statements":    strings.Replace(scenario, "    - {en: c, ja: c, answer: true, why: w}\n", "", 1),
	}
	for name, yml := range cases {
		if _, err := Load(lib(t, map[string]string{"t": yml})); err == nil {
			t.Errorf("%s: accepted", name)
		}
	}
}

// withScene is the scenario with a diagram added to it.
func withScene(scene string) string {
	return strings.Replace(scenario, "  statements:\n", "  scene:\n"+scene+"  statements:\n", 1)
}

func TestScenes(t *testing.T) {
	good := "    road: cross\n    night: true\n    things:\n" +
		"      - {is: you, at: [66, 100], blink: left}\n" +
		"      - {is: truck, at: [94, 20], heading: 180, label: truck, lights: true}\n" +
		"      - {is: light, at: [136, 12], color: green}\n" +
		"      - {is: arrow, via: [[66, 90], [62, 74], [20, 74]]}\n"
	banks, err := Load(lib(t, map[string]string{"t": withScene(good)}))
	if err != nil {
		t.Fatal(err)
	}
	if sc := banks["drive"].Question("sc-1").Scene; sc == nil || sc.Road != "cross" || len(sc.Things) != 4 || sc.Things[1].Heading != 180 {
		t.Fatalf("scene did not load: %+v", sc)
	}

	bad := map[string]string{
		"unknown road":  "    road: runway\n    things:\n      - {is: you, at: [66, 100]}\n",
		"unknown thing": "    road: straight\n    things:\n      - {is: you, at: [66, 100]}\n      - {is: tank, at: [94, 20]}\n",
		"nobody is you": "    road: straight\n    things:\n      - {is: car, at: [94, 20]}\n",
		"two of you":    "    road: straight\n    things:\n      - {is: you, at: [66, 100]}\n      - {is: you, at: [66, 60]}\n",
		"off the grid":  "    road: straight\n    things:\n      - {is: you, at: [66, 400]}\n",
		"no position":   "    road: straight\n    things:\n      - {is: you}\n",
		"bad heading":   "    road: straight\n    things:\n      - {is: you, at: [66, 100], heading: 400}\n",
		"light colour":  "    road: straight\n    things:\n      - {is: you, at: [66, 100]}\n      - {is: light, at: [130, 10], color: blue}\n",
		"short arrow":   "    road: straight\n    things:\n      - {is: you, at: [66, 100]}\n      - {is: arrow, via: [[66, 90]]}\n",
		"empty":         "    road: straight\n",
	}
	for name, scene := range bad {
		if _, err := Load(lib(t, map[string]string{"t": withScene(scene)})); err == nil {
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
	kari, _ := b.Exam("kari")
	qs, err := b.Draw(kari, rand.New(rand.NewPCG(1, 2)))
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
	hon, _ := b.Exam("hon")
	if _, err := b.Draw(hon, rand.New(rand.NewPCG(1, 2))); err == nil {
		t.Fatal("hon needs 90 + 5 scenarios; 60 should not be enough")
	}
}

func TestScoresScaleToTheExamsMax(t *testing.T) {
	banks, err := Load(lib(t, map[string]string{"t": tf("a", true, "kari")}))
	if err != nil {
		t.Fatal(err)
	}
	b := banks["drive"]
	for _, c := range []struct {
		exam           string
		earned, scaled int
	}{
		{"kari", 90, 90}, {"kari", 100, 100}, {"hon", 89, 89}, {"hon", 100, 100},
		{"mc", 3, 1000}, {"mc", 2, 667}, {"mc", 0, 0},
	} {
		spec, _ := b.Exam(c.exam)
		if got := Scale(spec, c.earned); got != c.scaled {
			t.Errorf("%s: %d points scaled to %d, want %d", c.exam, c.earned, got, c.scaled)
		}
	}
	// 47 of 65 is 723 out of 1,000: a pass at 720, as on the AWS exams.
	if got := Scale(Spec{Max: 1000, Draw: []content.ExamPart{{Kind: "choice", Count: 65, Points: 1}}}, 47); got != 723 {
		t.Errorf("47/65 scaled to %d", got)
	}
}

func TestChoiceQuestions(t *testing.T) {
	yml := `- {id: one, kind: choice, en: E, ja: J, why: W, ref: R, exams: [mc], options: [w, x, y, z], correct: [C]}
- {id: two, kind: choice, en: E, ja: J, why: W, ref: R, exams: [mc], options: [v, w, x, y, z], correct: [E, B]}
- {id: three, kind: choice, en: E, ja: J, why: W, ref: R, exams: [mc], options: [x, y, z], correct: [A]}
`
	banks, err := Load(lib(t, map[string]string{"t": yml}))
	if err != nil {
		t.Fatal(err)
	}
	b := banks["drive"]
	one, two := b.Question("one"), b.Question("two")
	if one.Choose != 1 || two.Choose != 2 {
		t.Fatalf("choose = %d, %d", one.Choose, two.Choose)
	}
	for _, c := range []struct {
		q     *Question
		picks []int
		ok    bool
	}{
		{one, []int{2}, true}, {one, []int{1}, false}, {one, nil, false}, {one, []int{2, 3}, false},
		{two, []int{1, 4}, true}, {two, []int{4, 1}, true}, {two, []int{1}, false}, {two, []int{1, 4, 0}, false},
		{two, []int{1, 1, 4}, true}, // a repeated pick is the same pick
	} {
		if got := Mark(c.q, Given{Picks: c.picks}); got != c.ok {
			t.Errorf("%s with %v: got %v", c.q.ID, c.picks, got)
		}
	}
	mc, _ := b.Exam("mc")
	qs, err := b.Draw(mc, rand.New(rand.NewPCG(3, 4)))
	if err != nil || len(qs) != 3 {
		t.Fatalf("drew %d, %v", len(qs), err)
	}
	if got := Points(mc, one); got != 1 {
		t.Errorf("a choice question in mc is worth %d", got)
	}
}

func TestPartsFromATopicAndShortfalls(t *testing.T) {
	track := strings.Replace(driveTrack, "draw: [{kind: choice, count: 3, points: 1}]",
		"draw: [{kind: choice, count: 1, points: 1, from: drive/rules/a}, {kind: choice, count: 2, points: 1, from: drive/rules/b}]", 1)
	q := func(id string) string {
		return "- {id: " + id + ", kind: choice, en: E, ja: J, why: W, ref: R, exams: [mc], options: [x, y, z], correct: [A]}\n"
	}
	root := t.TempDir()
	write := func(rel, s string) {
		path := filepath.Join(root, "drive", rel)
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, []byte(s), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	write("track.yaml", track)
	write("rules/a/lesson.md", "---\ntitle: A\nkind: quiz\norder: 1\n---\n")
	write("rules/a/questions.yaml", q("a1")+q("a2"))
	write("rules/b/lesson.md", "---\ntitle: B\nkind: quiz\norder: 2\n---\n")
	write("rules/b/questions.yaml", q("b1"))
	l, err := content.Load(root)
	if err != nil {
		t.Fatal(err)
	}
	banks, err := Load(l)
	if err != nil {
		t.Fatal(err)
	}
	mc, _ := banks["drive"].Exam("mc")
	short := banks["drive"].Shortfalls(mc)
	if len(short) != 1 || !strings.Contains(short[0], "1 of 2") {
		t.Fatalf("shortfalls = %v", short)
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
