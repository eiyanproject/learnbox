package httpapi

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/profiles"
	"github.com/eiyanproject/learnbox/internal/quiz"
	"github.com/eiyanproject/learnbox/internal/sandbox"
	"github.com/eiyanproject/learnbox/internal/term"
	"github.com/eiyanproject/learnbox/internal/workspace"
)

// quizServer serves a quiz track "drive" with one topic of 100 true/false
// questions (q000-q099; the even ones are true) and 6 scenarios whose
// statements are true, false, true.
func quizServer(t *testing.T) (http.Handler, *Server) {
	t.Helper()
	root := t.TempDir()
	dir := filepath.Join(root, "drive", "rules", "basics")
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	os.WriteFile(filepath.Join(root, "drive", "track.yaml"), []byte("title: Drive\ngroup: misc\nsections:\n  - id: rules\n    title: Rules\n"), 0o644)
	os.WriteFile(filepath.Join(dir, "lesson.md"), []byte("---\ntitle: Basics\nkind: quiz\n---\nNotes.\n"), 0o644)
	var y strings.Builder
	for i := range 100 {
		fmt.Fprintf(&y, "- {id: q%03d, en: E, ja: J, answer: %v, why: W, ref: R, exams: [kari, hon]}\n", i, i%2 == 0)
	}
	for i := range 6 {
		fmt.Fprintf(&y, "- id: s%d\n  kind: scenario\n  en: S\n  ja: S\n  ref: R\n  exams: [hon]\n  statements:\n", i)
		for _, a := range []bool{true, false, true} {
			fmt.Fprintf(&y, "    - {en: x, ja: x, answer: %v, why: w}\n", a)
		}
	}
	os.WriteFile(filepath.Join(dir, "questions.yaml"), []byte(y.String()), 0o644)

	lib, err := content.Load(root)
	if err != nil {
		t.Fatal(err)
	}
	banks, err := quiz.Load(lib)
	if err != nil {
		t.Fatal(err)
	}
	reg, _ := profiles.Open(t.TempDir())
	reg.AlsoDelete("quiz")
	sb := &sandbox.Sandbox{Home: t.TempDir()}
	ws, _ := workspace.New(sb)
	s := New(Deps{
		Log: slog.New(slog.DiscardHandler), WebDir: t.TempDir(), Lib: lib,
		Profiles: reg, Workspace: ws, Quiz: banks,
		Terms: term.NewManager(sb, slog.New(slog.DiscardHandler)),
	})
	return s.Handler(), s
}

func decode(t *testing.T, body string, v any) {
	t.Helper()
	if err := json.Unmarshal([]byte(body), v); err != nil {
		t.Fatalf("%v: %s", err, body)
	}
}

func TestAnswersAreMarkedOnTheServer(t *testing.T) {
	h, _ := quizServer(t)
	w := do(t, h, "GET", "/api/quiz/drive/topic/rules/basics", "")
	if w.Code != 200 {
		t.Fatalf("topic: %d %s", w.Code, w.Body)
	}
	if strings.Contains(w.Body.String(), `"answer"`) || strings.Contains(w.Body.String(), `"why"`) {
		t.Fatal("the topic must not send answers ahead")
	}
	var r struct {
		Result struct {
			Correct bool  `json:"correct"`
			Answer  *bool `json:"answer"`
			Why     string
		} `json:"result"`
	}
	decode(t, do(t, h, "POST", "/api/quiz/drive/answer", `{"id":"q000","answer":false}`).Body.String(), &r)
	if r.Result.Correct || r.Result.Answer == nil || !*r.Result.Answer {
		t.Fatalf("q000 is true; answering false: %+v", r.Result)
	}
	decode(t, do(t, h, "POST", "/api/quiz/drive/answer", `{"id":"s0","answers":[true,false,true]}`).Body.String(), &r)
	if !r.Result.Correct {
		t.Fatal("scenario answered right")
	}
	if w := do(t, h, "POST", "/api/quiz/drive/answer", `{"id":"nope","answer":true}`); w.Code != 404 {
		t.Fatalf("unknown question: %d", w.Code)
	}
}

func TestMistakesListWhatWasWrong(t *testing.T) {
	h, _ := quizServer(t)
	do(t, h, "POST", "/api/quiz/drive/answer", `{"id":"q001","answer":true}`) // q001 is false
	do(t, h, "POST", "/api/quiz/drive/answer", `{"id":"q002","answer":true}`) // right
	var m struct {
		Questions []struct{ ID string } `json:"questions"`
	}
	decode(t, do(t, h, "GET", "/api/quiz/drive/mistakes", "").Body.String(), &m)
	if len(m.Questions) != 1 || m.Questions[0].ID != "q001" {
		t.Fatalf("got %+v", m.Questions)
	}
}

func TestMasteringATopicPassesItsLesson(t *testing.T) {
	h, s := quizServer(t)
	b := s.Quiz["drive"]
	var last struct {
		Mastered bool `json:"topic_mastered"`
	}
	for _, q := range b.Questions {
		body := fmt.Sprintf(`{"id":%q,"answer":%v}`, q.ID, q.Answer != nil && *q.Answer)
		if q.Scenario() {
			body = fmt.Sprintf(`{"id":%q,"answers":[true,false,true]}`, q.ID)
		}
		decode(t, do(t, h, "POST", "/api/quiz/drive/answer", body).Body.String(), &last)
	}
	if !last.Mastered {
		t.Fatal("the last right answer should report the topic mastered")
	}
	store, _ := s.Profiles.Progress(profiles.DefaultID)
	if store.Get("drive/rules/basics").Status != "passed" {
		t.Fatal("lesson not marked passed")
	}
}

type examResp struct {
	Deadline  time.Time `json:"deadline"`
	Questions []struct {
		ID   string `json:"id"`
		Kind string `json:"kind"`
	} `json:"questions"`
	Result struct {
		Score    int  `json:"score"`
		Passed   bool `json:"passed"`
		Overtime bool `json:"overtime"`
	} `json:"result"`
}

func TestExamResumesInsteadOfRedrawing(t *testing.T) {
	h, _ := quizServer(t)
	var a, b examResp
	decode(t, do(t, h, "POST", "/api/quiz/drive/exam/kari", "").Body.String(), &a)
	decode(t, do(t, h, "POST", "/api/quiz/drive/exam/kari", "").Body.String(), &b)
	if len(a.Questions) != 50 || !a.Deadline.Equal(b.Deadline) || a.Questions[0].ID != b.Questions[0].ID {
		t.Fatal("a reload must get the same questions and clock")
	}
	var hon examResp
	decode(t, do(t, h, "POST", "/api/quiz/drive/exam/hon", "").Body.String(), &hon)
	sc := 0
	for _, q := range hon.Questions {
		if q.Kind == "scenario" {
			sc++
		}
	}
	if len(hon.Questions) != 95 || sc != 5 {
		t.Fatalf("hon drew %d questions, %d scenarios", len(hon.Questions), sc)
	}
}

// answersFor builds a submission answering every question right, except the
// first `wrong` true/false ones.
func answersFor(s *Server, e examResp, wrong int) string {
	b := s.Quiz["drive"]
	parts := []string{}
	for _, q := range e.Questions {
		qq := b.Question(q.ID)
		if qq.Scenario() {
			parts = append(parts, fmt.Sprintf(`%q:{"answers":[true,false,true]}`, q.ID))
			continue
		}
		a := *qq.Answer
		if wrong > 0 {
			a, wrong = !a, wrong-1
		}
		parts = append(parts, fmt.Sprintf(`%q:{"answer":%v}`, q.ID, a))
	}
	return `{"answers":{` + strings.Join(parts, ",") + `}}`
}

func TestExamScoringFollowsTheRealRules(t *testing.T) {
	h, s := quizServer(t)
	var e, r examResp
	// 仮免: 2 points each. Five wrong is 90, a pass; six wrong is 88, a fail.
	decode(t, do(t, h, "POST", "/api/quiz/drive/exam/kari", "").Body.String(), &e)
	decode(t, do(t, h, "POST", "/api/quiz/drive/exam/kari/submit", answersFor(s, e, 5)).Body.String(), &r)
	if r.Result.Score != 90 || !r.Result.Passed {
		t.Fatalf("five wrong: %+v", r.Result)
	}
	decode(t, do(t, h, "POST", "/api/quiz/drive/exam/kari", "").Body.String(), &e)
	decode(t, do(t, h, "POST", "/api/quiz/drive/exam/kari/submit", answersFor(s, e, 6)).Body.String(), &r)
	if r.Result.Score != 88 || r.Result.Passed {
		t.Fatalf("six wrong: %+v", r.Result)
	}
	// 本免: 90 x 1 + 5 x 2. All right is 100.
	decode(t, do(t, h, "POST", "/api/quiz/drive/exam/hon", "").Body.String(), &e)
	decode(t, do(t, h, "POST", "/api/quiz/drive/exam/hon/submit", answersFor(s, e, 0)).Body.String(), &r)
	if r.Result.Score != 100 || !r.Result.Passed {
		t.Fatalf("all right: %+v", r.Result)
	}
	if w := do(t, h, "POST", "/api/quiz/drive/exam/hon/submit", `{"answers":{}}`); w.Code != http.StatusConflict {
		t.Fatalf("submitting with no exam running: %d", w.Code)
	}
}

func TestOvertimeFailsWhateverTheScore(t *testing.T) {
	h, s := quizServer(t)
	var e, r examResp
	decode(t, do(t, h, "POST", "/api/quiz/drive/exam/kari", "").Body.String(), &e)
	// Move the deadline into the past, as if the clock ran out.
	st, _ := s.quizStore(profiles.DefaultID)
	a, _ := st.Active("drive", "kari")
	a.Started = a.Started.Add(-40 * time.Minute)
	a.Deadline = a.Deadline.Add(-40 * time.Minute)
	st.Start("drive", a)
	decode(t, do(t, h, "POST", "/api/quiz/drive/exam/kari/submit", answersFor(s, e, 0)).Body.String(), &r)
	if !r.Result.Overtime || r.Result.Passed || r.Result.Score != 100 {
		t.Fatalf("got %+v", r.Result)
	}
}

func TestQuizOverviewCountsMastery(t *testing.T) {
	h, _ := quizServer(t)
	do(t, h, "POST", "/api/quiz/drive/answer", `{"id":"q000","answer":true}`)
	do(t, h, "POST", "/api/quiz/drive/answer", `{"id":"q001","answer":true}`)
	var o struct {
		Mistakes int `json:"mistakes"`
		Sections []struct {
			Topics []struct{ Total, Mastered, Mistakes int } `json:"topics"`
		} `json:"sections"`
		Exams []struct {
			ID    string `json:"id"`
			Ready bool   `json:"ready"`
		} `json:"exams"`
	}
	decode(t, do(t, h, "GET", "/api/quiz/drive", "").Body.String(), &o)
	tp := o.Sections[0].Topics[0]
	if tp.Total != 106 || tp.Mastered != 1 || tp.Mistakes != 1 || o.Mistakes != 1 {
		t.Fatalf("got %+v mistakes=%d", tp, o.Mistakes)
	}
	if len(o.Exams) != 2 || !o.Exams[0].Ready || !o.Exams[1].Ready {
		t.Fatalf("exams: %+v", o.Exams)
	}
}
