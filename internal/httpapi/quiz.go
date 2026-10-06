package httpapi

import (
	"encoding/json"
	"math/rand/v2"
	"net/http"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/progress"
	"github.com/eiyanproject/learnbox/internal/quiz"
)

// Quiz endpoints. Answers are marked here, never sent ahead: the client gets a
// question's text, and learns the answer and the rule behind it only after
// answering.
//
//	GET    /api/quiz/{track}                         overview: topics, mastery, exams, history
//	GET    /api/quiz/{track}/topic/{section}/{slug}  a topic's notes and questions
//	POST   /api/quiz/{track}/answer                  mark one answer {id, answer|answers}
//	GET    /api/quiz/{track}/mistakes                questions in the mistakes review
//	POST   /api/quiz/{track}/exam/{exam}             start (or resume) a mock exam
//	POST   /api/quiz/{track}/exam/{exam}/submit      finish it: {answers: {id: given}}
//	DELETE /api/quiz/{track}/exam/{exam}             abandon it
func (s *Server) quizRoutes(m *http.ServeMux) {
	const T = "/api/quiz/{track}"
	m.HandleFunc("GET "+T, s.quizOverview)
	m.HandleFunc("GET "+T+"/topic/{section}/{slug}", s.quizTopic)
	m.HandleFunc("POST "+T+"/answer", s.quizAnswer)
	m.HandleFunc("GET "+T+"/mistakes", s.quizMistakes)
	m.HandleFunc("POST "+T+"/exam/{exam}", s.quizStartExam)
	m.HandleFunc("POST "+T+"/exam/{exam}/submit", s.quizSubmitExam)
	m.HandleFunc("DELETE "+T+"/exam/{exam}", s.quizAbandonExam)
}

// overtimeGrace is how long after the deadline a submission still counts as
// on time: the browser submits at zero, and the request takes a moment.
const overtimeGrace = 30 * time.Second

// quizFor resolves the track's bank and the profile's quiz record.
func (s *Server) quizFor(w http.ResponseWriter, r *http.Request) (*quiz.Bank, *viewer, *quiz.Store) {
	b := s.Quiz[r.PathValue("track")]
	if b == nil {
		writeErr(w, http.StatusNotFound, "no such quiz track")
		return nil, nil, nil
	}
	v := s.who(w, r)
	if v == nil {
		return nil, nil, nil
	}
	st, err := s.quizStore(v.ID)
	if err != nil {
		s.fail(w, "quiz", err)
		return nil, nil, nil
	}
	return b, v, st
}

func (s *Server) quizStore(profile string) (*quiz.Store, error) {
	s.quizMu.Lock()
	defer s.quizMu.Unlock()
	if s.quizStores == nil {
		s.quizStores = map[string]*quiz.Store{}
	}
	if st := s.quizStores[profile]; st != nil {
		return st, nil
	}
	st, err := quiz.Open(s.Profiles.DataFile(profile, "quiz"))
	if err != nil {
		return nil, err
	}
	s.quizStores[profile] = st
	return st, nil
}

func (s *Server) forgetQuizStore(profile string) {
	s.quizMu.Lock()
	delete(s.quizStores, profile)
	s.quizMu.Unlock()
}

// ---------- overview ----------

type quizExamOut struct {
	quiz.Spec
	Pool       int           `json:"pool"`
	ScPool     int           `json:"scenario_pool"`
	Ready      bool          `json:"ready"`
	Deadline   time.Time     `json:"deadline,omitzero"` // set while one is running
	Best       *quiz.Result  `json:"best,omitempty"`
	Recent     []quiz.Result `json:"recent"`
	Attempts   int           `json:"attempts"`
	PassStreak int           `json:"pass_streak"` // passes in a row, newest first
}

func (s *Server) quizOverview(w http.ResponseWriter, r *http.Request) {
	b, _, st := s.quizFor(w, r)
	if b == nil {
		return
	}
	t := s.track(b.Track)
	recs := st.Records(b.Track)

	type topicOut struct {
		ID       string `json:"id"`
		Title    string `json:"title"`
		Summary  string `json:"summary"`
		Total    int    `json:"total"`
		Mastered int    `json:"mastered"` // answered right at least once
		Mistakes int    `json:"mistakes"`
	}
	type sectionOut struct {
		ID     string     `json:"id"`
		Title  string     `json:"title"`
		Topics []topicOut `json:"topics"`
	}
	sections := []sectionOut{}
	mistakes := 0
	for _, sec := range t.Sections {
		so := sectionOut{ID: sec.ID, Title: sec.Title, Topics: []topicOut{}}
		for _, l := range sec.Lessons {
			if l.Kind != "quiz" {
				continue
			}
			to := topicOut{ID: l.ID(), Title: l.Title, Summary: l.Summary}
			for _, q := range b.Topic(l.ID()) {
				to.Total++
				rec := recs[q.ID]
				if rec.Right > 0 {
					to.Mastered++
				}
				if rec.Mistake() {
					to.Mistakes++
					mistakes++
				}
			}
			so.Topics = append(so.Topics, to)
		}
		sections = append(sections, so)
	}

	history := st.Results(b.Track)
	exams := []quizExamOut{}
	for _, id := range quiz.SpecOrder {
		spec := quiz.Specs[id]
		tf, sc := b.Pool(id)
		eo := quizExamOut{Spec: spec, Pool: len(tf), ScPool: len(sc), Recent: []quiz.Result{}}
		eo.Ready = len(tf) >= spec.TF && len(sc) >= spec.Scenarios
		if a, ok := st.Active(b.Track, id); ok {
			eo.Deadline = a.Deadline
		}
		streakOpen := true
		for _, res := range history {
			if res.Exam != id {
				continue
			}
			eo.Attempts++
			if len(eo.Recent) < 5 {
				eo.Recent = append(eo.Recent, res)
			}
			if eo.Best == nil || res.Score > eo.Best.Score {
				best := res
				eo.Best = &best
			}
			if streakOpen && res.Passed && !res.Overtime {
				eo.PassStreak++
			} else {
				streakOpen = false
			}
		}
		exams = append(exams, eo)
	}

	writeJSON(w, http.StatusOK, map[string]any{
		"track": b.Track, "title": t.Title, "description": t.Description,
		"sections": sections, "exams": exams, "mistakes": mistakes,
		"total": len(b.Questions), "clear_after": quiz.ClearAfter,
	})
}

func (s *Server) track(lang string) *content.Track {
	for _, t := range s.Lib.Tracks {
		if t.Lang == lang {
			return t
		}
	}
	return nil
}

// ---------- topic study ----------

func (s *Server) quizTopic(w http.ResponseWriter, r *http.Request) {
	b, v, st := s.quizFor(w, r)
	if b == nil {
		return
	}
	id := b.Track + "/" + r.PathValue("section") + "/" + r.PathValue("slug")
	l := s.Lib.Lesson(id)
	if l == nil || l.Kind != "quiz" {
		writeErr(w, http.StatusNotFound, "no such topic")
		return
	}
	if _, err := v.Progress.Opened(l.ID()); err != nil {
		s.fail(w, "progress", err)
		return
	}
	notes, err := content.RenderMarkdown(l.Body)
	if err != nil {
		s.fail(w, "markdown", err)
		return
	}
	recs := st.Records(b.Track)
	type qOut struct {
		*quiz.Question
		Mistake bool `json:"mistake"`
		Right   bool `json:"right_before"`
	}
	qs := []qOut{}
	for _, q := range b.Topic(l.ID()) {
		qs = append(qs, qOut{Question: q, Mistake: recs[q.ID].Mistake(), Right: recs[q.ID].Right > 0})
	}
	prev, next := s.Lib.Neighbours(l.ID())
	link := func(x *content.Lesson) any {
		if x == nil || x.Kind != "quiz" {
			return nil
		}
		return map[string]string{"id": x.ID(), "title": x.Title}
	}
	writeJSON(w, http.StatusOK, map[string]any{
		"id": l.ID(), "title": l.Title, "summary": l.Summary, "notes_html": notes,
		"track": b.Track, "track_title": s.track(b.Track).Title,
		"questions": qs, "prev": link(prev), "next": link(next),
	})
}

// ---------- answering ----------

type answerIn struct {
	ID string `json:"id"`
	quiz.Given
}

// explanation is what a learner sees once a question is answered.
type explanation struct {
	ID         string         `json:"id"`
	Correct    bool           `json:"correct"`
	Answer     *bool          `json:"answer,omitempty"`
	Why        string         `json:"why,omitempty"`
	Ref        string         `json:"ref"`
	Statements []statementOut `json:"statements,omitempty"`
	Given      *quiz.Given    `json:"given,omitempty"`
	Question   *quiz.Question `json:"question,omitempty"`
}

type statementOut struct {
	EN     string `json:"en"`
	JA     string `json:"ja"`
	Answer bool   `json:"answer"`
	Why    string `json:"why"`
}

func explain(q *quiz.Question, correct bool) explanation {
	e := explanation{ID: q.ID, Correct: correct, Ref: q.Ref}
	if q.Scenario() {
		for _, st := range q.Statements {
			e.Statements = append(e.Statements, statementOut{EN: st.EN, JA: st.JA, Answer: *st.Answer, Why: st.Why})
		}
	} else {
		e.Answer, e.Why = q.Answer, q.Why
	}
	return e
}

func (s *Server) quizAnswer(w http.ResponseWriter, r *http.Request) {
	b, v, st := s.quizFor(w, r)
	if b == nil {
		return
	}
	var in answerIn
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 4<<10)).Decode(&in); err != nil {
		writeErr(w, http.StatusBadRequest, `body must be {"id": string, "answer": bool} or {"id": string, "answers": [bool, bool, bool]}`)
		return
	}
	q := b.Question(in.ID)
	if q == nil {
		writeErr(w, http.StatusNotFound, "no such question")
		return
	}
	ok := quiz.Mark(q, in.Given)
	if err := st.Answered(b.Track, map[string]bool{q.ID: ok}, time.Now().UTC()); err != nil {
		s.fail(w, "quiz", err)
		return
	}
	topicDone, err := s.markTopicIfMastered(b, v, st, q.Topic)
	if err != nil {
		s.fail(w, "progress", err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"result": explain(q, ok), "topic_mastered": topicDone})
}

// markTopicIfMastered marks a topic's lesson passed once every question in it
// has been answered right at least once, so it shows as done in the track
// like any lesson. It reports whether this call is the one that did it.
func (s *Server) markTopicIfMastered(b *quiz.Bank, v *viewer, st *quiz.Store, topic string) (bool, error) {
	recs := st.Records(b.Track)
	for _, q := range b.Topic(topic) {
		if recs[q.ID].Right == 0 {
			return false, nil
		}
	}
	newly := false
	_, err := v.Progress.Update(topic, func(e *progress.Entry) {
		if e.Status != progress.Passed {
			e.Status = progress.Passed
			e.PassedAt = time.Now().UTC()
			newly = true
		}
	})
	return newly, err
}

func (s *Server) quizMistakes(w http.ResponseWriter, r *http.Request) {
	b, _, st := s.quizFor(w, r)
	if b == nil {
		return
	}
	recs := st.Records(b.Track)
	qs := []*quiz.Question{}
	for _, q := range b.Questions {
		if recs[q.ID].Mistake() {
			qs = append(qs, q)
		}
	}
	// Least recently seen first, so a long list rotates rather than repeating
	// the same opening questions every visit.
	sortByLastSeen(qs, recs)
	writeJSON(w, http.StatusOK, map[string]any{"questions": qs, "clear_after": quiz.ClearAfter})
}

func sortByLastSeen(qs []*quiz.Question, recs map[string]quiz.Record) {
	for i := 1; i < len(qs); i++ {
		for j := i; j > 0 && recs[qs[j].ID].LastSeen.Before(recs[qs[j-1].ID].LastSeen); j-- {
			qs[j], qs[j-1] = qs[j-1], qs[j]
		}
	}
}

// ---------- mock exams ----------

func (s *Server) examSpec(w http.ResponseWriter, r *http.Request) (quiz.Spec, bool) {
	spec, ok := quiz.Specs[r.PathValue("exam")]
	if !ok {
		writeErr(w, http.StatusNotFound, "no such exam")
	}
	return spec, ok
}

func (s *Server) quizStartExam(w http.ResponseWriter, r *http.Request) {
	b, _, st := s.quizFor(w, r)
	if b == nil {
		return
	}
	spec, ok := s.examSpec(w, r)
	if !ok {
		return
	}
	now := time.Now().UTC()
	a, running := st.Active(b.Track, spec.ID)
	// A running exam is resumed until its deadline (plus the grace) has
	// passed; after that a fresh one is drawn. Reloading the page must not
	// buy a new set of questions or a new clock.
	if !running || now.After(a.Deadline.Add(overtimeGrace)) {
		qs, err := b.Draw(spec, rand.New(rand.NewPCG(uint64(now.UnixNano()), rand.Uint64())))
		if err != nil {
			writeErr(w, http.StatusConflict, err.Error())
			return
		}
		a = quiz.Active{Exam: spec.ID, Started: now, Deadline: now.Add(time.Duration(spec.Minutes) * time.Minute)}
		for _, q := range qs {
			a.IDs = append(a.IDs, q.ID)
		}
		if err := st.Start(b.Track, a); err != nil {
			s.fail(w, "quiz", err)
			return
		}
	}
	qs := []*quiz.Question{}
	for _, id := range a.IDs {
		if q := b.Question(id); q != nil {
			qs = append(qs, q)
		}
	}
	writeJSON(w, http.StatusOK, map[string]any{
		"spec": spec, "started": a.Started, "deadline": a.Deadline, "now": now, "questions": qs,
	})
}

func (s *Server) quizSubmitExam(w http.ResponseWriter, r *http.Request) {
	b, _, st := s.quizFor(w, r)
	if b == nil {
		return
	}
	spec, ok := s.examSpec(w, r)
	if !ok {
		return
	}
	a, running := st.Active(b.Track, spec.ID)
	if !running {
		writeErr(w, http.StatusConflict, "no exam is running; start one first")
		return
	}
	var in struct {
		Answers map[string]quiz.Given `json:"answers"`
	}
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 64<<10)).Decode(&in); err != nil {
		writeErr(w, http.StatusBadRequest, `body must be {"answers": {"<id>": {"answer": bool} | {"answers": [bool, bool, bool]}}}`)
		return
	}
	now := time.Now().UTC()
	res := quiz.Result{Track: b.Track, Exam: spec.ID, At: now, Max: spec.Max,
		Seconds: int(now.Sub(a.Started).Seconds()), Overtime: now.After(a.Deadline.Add(overtimeGrace))}
	correct := map[string]bool{}
	review := []explanation{}
	for _, id := range a.IDs {
		q := b.Question(id)
		if q == nil {
			continue // removed from the bank since the exam began
		}
		g, answered := in.Answers[id]
		right := quiz.Mark(q, g)
		correct[id] = right
		if right {
			res.Score += quiz.Points(spec, q)
		} else {
			res.Wrong = append(res.Wrong, id)
		}
		e := explain(q, right)
		e.Question = q
		if answered {
			given := g
			e.Given = &given
		}
		review = append(review, e)
	}
	// Over time is a fail however high the score: the real test stops at the
	// bell. The score is still shown, so the practice is not wasted.
	res.Passed = res.Score >= spec.Pass && !res.Overtime
	if err := st.Finish(res, correct); err != nil {
		s.fail(w, "quiz", err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"result": res, "review": review})
}

func (s *Server) quizAbandonExam(w http.ResponseWriter, r *http.Request) {
	b, _, st := s.quizFor(w, r)
	if b == nil {
		return
	}
	spec, ok := s.examSpec(w, r)
	if !ok {
		return
	}
	if err := st.Abandon(b.Track, spec.ID); err != nil {
		s.fail(w, "quiz", err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"status": "abandoned"})
}
