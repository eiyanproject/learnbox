import {
  api,
  ApiError,
  quizHref,
  type ExamResult,
  type ExamStart,
  type QuizExplanation,
  type QuizGiven,
  type QuizOverview,
  type QuizQuestion,
  type QuizScene,
  type Track,
} from "../api";
import { sceneFigure } from "../components/scene";
import { append, clear, h, html, toast } from "../dom";
import { navigate, type Page } from "../router";
import type { Shell } from "../shell";

const msg = (e: unknown) => (e instanceof Error ? e.message : String(e));

function go(href: string) {
  return (e: Event) => {
    e.preventDefault();
    navigate(href);
  };
}

function failPage(root: HTMLElement, title: string, e: unknown) {
  clear(root);
  root.append(h("div", { class: "empty" }, h("h2", null, title), h("p", null, msg(e))));
}

const mmss = (secs: number) => {
  const s = Math.max(0, Math.round(secs));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
};

// ○ is true and × is false: the marks the Japanese test itself uses.
const MARK = (b: boolean) => (b ? "○" : "×");
const WORD = (b: boolean) => (b ? "True" : "False");

/**
 * The picture that goes with a question. It is fetched from where it is
 * hosted, so it may not arrive (no internet, or the host is down): then it
 * takes itself away and the wording carries the question alone.
 */
function questionImage(src: string): HTMLElement {
  const fig = h("figure", { class: "q-img" });
  const img = h("img", { src, alt: "The sign or picture this question is about", loading: "lazy", decoding: "async", referrerpolicy: "no-referrer" }) as HTMLImageElement;
  img.addEventListener("error", () => fig.remove());
  fig.append(img);
  return fig;
}

/** The question text: English, with the Japanese underneath. */
function questionText(q: { en: string; ja: string; image?: string; scene?: QuizScene }, cls = "q-text") {
  const text = h("div", { class: "q-words" }, h("p", { class: "q-en" }, q.en), h("p", { class: "q-ja", lang: "ja" }, q.ja));
  if (q.scene) return h("div", { class: `${cls} has-scene` }, sceneFigure(q.scene), text);
  return h("div", { class: q.image ? `${cls} has-img` : cls }, q.image ? questionImage(q.image) : null, text);
}

function tfButtons(onPick: (v: boolean) => void, chosen?: boolean, disabled = false) {
  const mk = (v: boolean) =>
    h(
      "button",
      {
        class: `tf ${v ? "maru" : "batsu"}${chosen === v ? " on" : ""}`,
        disabled,
        title: `${WORD(v)}  (${v ? "O or 1" : "X or 2"})`,
        onclick: () => onPick(v),
      },
      h("span", { class: "mark" }, MARK(v)),
      h("span", { class: "word" }, WORD(v)),
    );
  return h("div", { class: "tf-row" }, mk(true), mk(false));
}

/** What the learner sees once a question is marked. */
function feedback(e: QuizExplanation): HTMLElement {
  const box = h("div", { class: `q-feedback ${e.correct ? "ok" : "bad"}` }, h("p", { class: "verdict" }, e.correct ? "Correct" : "Not quite"));
  if (e.statements) {
    e.statements.forEach((s, i) => {
      const given = e.given?.answers?.[i];
      box.append(
        h(
          "div",
          { class: "stmt-why" },
          h("p", null, h("strong", null, `${i + 1}. ${MARK(s.answer)} `), s.en, given !== undefined && given !== s.answer ? h("span", { class: "you" }, ` (you: ${MARK(given)})`) : null),
          h("p", { class: "why" }, s.why),
        ),
      );
    });
  } else {
    box.append(
      h("p", null, "The answer is ", h("strong", null, `${MARK(!!e.answer)} ${WORD(!!e.answer)}`), "."),
      h("p", { class: "why" }, e.why ?? ""),
    );
  }
  box.append(h("p", { class: "ref lbl", lang: "ja" }, e.ref));
  return box;
}

/**
 * One question to answer. For true/false a press answers it; a scenario takes
 * a mark for each of its three statements, then a confirm.
 */
function questionCard(q: QuizQuestion, opts: { label: string; onAnswer: (g: QuizGiven) => Promise<QuizExplanation | null>; onNext: () => void; nextLabel: string }) {
  const card = h("section", { class: "q-card panel" });
  const head = h("div", { class: "q-head" }, h("span", { class: "lbl" }, opts.label), q.kind === "scenario" ? h("span", { class: "badge started" }, "scenario · 3 parts") : null);
  const body = h("div", { class: "q-body" });
  const after = h("div", { class: "q-after" });
  card.append(head, body, after);

  let done = false;
  const finish = async (g: QuizGiven) => {
    if (done) return;
    done = true;
    const e = await opts.onAnswer(g);
    if (!e) {
      done = false;
      return;
    }
    draw(g);
    after.replaceChildren(feedback(e), h("div", { class: "q-next" }, h("button", { class: "btn primary", onclick: opts.onNext, "data-next": "1" }, opts.nextLabel)));
    (after.querySelector("[data-next]") as HTMLElement | null)?.focus();
  };

  const picks: (boolean | undefined)[] = [undefined, undefined, undefined];
  const draw = (answered?: QuizGiven) => {
    clear(body);
    body.append(questionText(q));
    if (q.kind !== "scenario") {
      body.append(tfButtons((v) => void finish({ answer: v }), answered?.answer, !!answered));
      return;
    }
    (q.statements ?? []).forEach((s, i) => {
      body.append(
        h(
          "div",
          { class: "stmt" },
          h("span", { class: "stmt-n" }, String(i + 1)),
          questionText(s, "q-text small"),
          tfButtons(
            (v) => {
              picks[i] = v;
              draw();
            },
            answered ? answered.answers?.[i] : picks[i],
            !!answered,
          ),
        ),
      );
    });
    if (!answered) {
      const ready = picks.every((p) => p !== undefined);
      body.append(
        h("div", { class: "q-next" }, h("button", { class: "btn primary", disabled: !ready, onclick: () => void finish({ answers: picks as boolean[] }) }, "Check all three")),
      );
    }
  };
  draw();

  // Keyboard: O / 1 for true, X / 2 for false, Enter for next.
  const keys = (e: KeyboardEvent) => {
    if ((e.target as HTMLElement).closest("input, textarea")) return;
    if (!done && q.kind !== "scenario") {
      if (e.key === "o" || e.key === "O" || e.key === "1") void finish({ answer: true });
      if (e.key === "x" || e.key === "X" || e.key === "2") void finish({ answer: false });
    } else if (done && e.key === "Enter") {
      e.preventDefault();
      opts.onNext();
    }
  };
  document.addEventListener("keydown", keys);
  return { el: card, dispose: () => document.removeEventListener("keydown", keys) };
}

// ---------- the Misc area ----------

export async function miscPage(shell: Shell): Promise<Page> {
  shell.setActive("misc");
  shell.setFill(false);
  const root = shell.content;
  clear(root);
  let tracks: Track[];
  try {
    tracks = (await api.tracks()).tracks.filter((t) => t.group === "misc");
  } catch (e) {
    failPage(root, "Cannot reach the server", e);
    return {};
  }
  root.replaceChildren(
    h("div", { class: "headrow" }, h("div", null, h("h1", null, "Misc"), h("p", { class: "sub" }, "Things worth learning that are not programming."))),
    h(
      "section",
      { class: "panel" },
      ...(tracks.length
        ? tracks.map((t) =>
            h(
              "a",
              { class: "track-card", href: `/quiz/${t.lang}`, onclick: go(`/quiz/${t.lang}`) },
              h("div", null, h("h3", null, t.title), h("p", null, t.description)),
              h("span", { class: "num", style: "font-size:22px;font-weight:600" }, `${t.total ? Math.round((t.passed / t.total) * 100) : 0}%`),
            ),
          )
        : [h("div", { class: "empty" }, h("h2", null, "Nothing here yet"))]),
    ),
  );
  return {};
}

// ---------- a quiz track's overview ----------

export async function quizHomePage(shell: Shell, track: string): Promise<Page> {
  shell.setActive("misc");
  shell.setFill(false);
  const root = shell.content;
  clear(root);
  root.append(h("div", { class: "skel" }), h("div", { class: "skel", style: "height:300px" }));
  let o: QuizOverview;
  try {
    o = await api.quiz(track);
  } catch (e) {
    failPage(root, e instanceof ApiError && e.status === 404 ? "No such quiz" : "Could not load the quiz", e);
    return {};
  }

  const mastered = o.sections.reduce((n, s) => n + s.topics.reduce((m, t) => m + t.mastered, 0), 0);
  const firstTodo = o.sections.flatMap((s) => s.topics).find((t) => t.mastered < t.total);

  const examCard = (e: QuizOverview["exams"][number]) => {
    const running = e.deadline && new Date(e.deadline).getTime() > Date.now();
    const lines = [`${e.tf} true/false`];
    if (e.scenarios) lines.push(`${e.scenarios} scenarios`);
    return h(
      "div",
      { class: "exam-card" },
      h("h3", null, e.title),
      h("p", { class: "sub" }, `${lines.join(" + ")} · ${e.minutes} min · pass ${e.pass}/${e.max}`),
      h(
        "p",
        { class: "lbl" },
        e.best ? `best ${e.best.score} · ${e.attempts} attempt${e.attempts === 1 ? "" : "s"}${e.pass_streak ? ` · ${e.pass_streak} pass${e.pass_streak === 1 ? "" : "es"} in a row` : ""}` : "not attempted yet",
      ),
      e.recent.length ? h("div", { class: "exam-dots", title: "Recent results, newest first" }, ...e.recent.map((r) => h("i", { class: r.passed ? "p" : "f", title: `${r.score}/${r.max}` }))) : null,
      e.ready
        ? h("a", { class: "btn primary", href: `/quiz/${track}/exam/${e.id}`, onclick: go(`/quiz/${track}/exam/${e.id}`) }, running ? "Resume exam" : "Start mock exam")
        : h("span", { class: "lbl" }, `needs ${e.tf} + ${e.scenarios}; has ${e.pool} + ${e.scenario_pool}`),
    );
  };

  root.replaceChildren(
    h(
      "div",
      { class: "headrow" },
      h("div", null, h("span", { class: "lbl" }, `Misc · ${mastered} of ${o.total} questions answered right`), h("h1", null, o.title), h("p", { class: "sub" }, o.description)),
      firstTodo ? h("a", { class: "btn primary", href: quizHref(firstTodo.id), onclick: go(quizHref(firstTodo.id)) }, "Continue studying") : null,
    ),
    h(
      "div",
      { class: "quiz-top" },
      ...o.exams.map(examCard),
      h(
        "div",
        { class: "exam-card" },
        h("h3", null, "Mistakes review"),
        h("p", { class: "sub" }, `Questions you got wrong. Answer one right ${o.clear_after} times in a row to clear it.`),
        h("p", { class: "num", style: "font-size:28px;font-weight:600" }, String(o.mistakes)),
        o.mistakes
          ? h("a", { class: "btn am", href: `/quiz/${track}/mistakes`, onclick: go(`/quiz/${track}/mistakes`) }, "Review mistakes")
          : h("span", { class: "lbl" }, "nothing to review"),
      ),
    ),
    ...o.sections
      .filter((s) => s.topics.length)
      .map((s) =>
        h(
          "section",
          { class: "panel", style: "margin-top:18px" },
          h("div", { class: "phead" }, h("h2", null, s.title)),
          ...s.topics.map((t, i) =>
            h(
              "a",
              { class: "row", href: quizHref(t.id), onclick: go(quizHref(t.id)) },
              h("span", { class: "idx" }, String(i + 1).padStart(2, "0")),
              h("div", { style: "min-width:0" }, h("p", { class: "rt" }, t.title), h("p", { class: "rd" }, t.summary)),
              h("span", { class: "hide-sm" }, h("span", { class: "meter", style: "width:90px" }, h("i", { style: `width:${t.total ? (t.mastered / t.total) * 100 : 0}%` }))),
              h(
                "span",
                { class: "right" },
                t.mistakes ? h("span", { class: "badge started" }, `${t.mistakes} to review`) : null,
                h("span", { class: t.mastered === t.total ? "badge passed" : "badge" }, `${t.mastered}/${t.total}`),
              ),
            ),
          ),
        ),
      ),
  );
  return {};
}

// ---------- studying: one topic, or the mistakes review ----------

export async function quizStudyPage(shell: Shell, track: string, section: string | null, slug: string | null): Promise<Page> {
  shell.setActive("misc");
  shell.setFill(false);
  const root = shell.content;
  clear(root);
  root.append(h("div", { class: "skel" }), h("div", { class: "skel", style: "height:300px" }));

  const reviewing = section === null;
  let title: string, notesHTML = "", questions: QuizQuestion[];
  let next: { id: string; title: string } | null = null;
  try {
    if (reviewing) {
      const r = await api.quizMistakes(track);
      title = "Mistakes review";
      questions = r.questions;
    } else {
      const t = await api.quizTopic(track, section!, slug!);
      title = t.title;
      notesHTML = t.notes_html;
      questions = t.questions;
      next = t.next;
    }
  } catch (e) {
    failPage(root, "Could not load the questions", e);
    return {};
  }

  const back = `/quiz/${track}`;
  let i = 0;
  const wrong: QuizQuestion[] = [];
  let right = 0;
  let card: { el: HTMLElement; dispose: () => void } | null = null;
  const stage = h("div", { class: "quiz-stage" });

  const summary = () => {
    card?.dispose();
    card = null;
    stage.replaceChildren(
      h(
        "section",
        { class: "q-card panel" },
        h("div", { class: "q-body" }, h("h2", null, `${right} of ${right + wrong.length} right`)),
        h(
          "div",
          { class: "q-next pad" },
          wrong.length
            ? h(
                "button",
                {
                  class: "btn am",
                  onclick: () => {
                    questions = wrong.splice(0);
                    i = 0;
                    right = 0;
                    show();
                  },
                },
                `Try the ${wrong.length} wrong one${wrong.length === 1 ? "" : "s"} again`,
              )
            : null,
          next && !reviewing ? h("a", { class: "btn primary", href: quizHref(next.id), onclick: go(quizHref(next.id)) }, `Next: ${next.title}`) : null,
          h("a", { class: "btn", href: back, onclick: go(back) }, "Back to overview"),
        ),
      ),
    );
    shell.invalidateTracks();
  };

  const show = () => {
    card?.dispose();
    if (i >= questions.length) {
      summary();
      return;
    }
    const q = questions[i];
    card = questionCard(q, {
      label: `${reviewing ? "Review" : "Question"} ${i + 1} of ${questions.length}`,
      nextLabel: i + 1 < questions.length ? "Next question" : "See results",
      onAnswer: async (g) => {
        try {
          const r = await api.quizAnswer(track, q.id, g);
          if (r.result.correct) right++;
          else wrong.push(q);
          if (r.topic_mastered) toast("Topic mastered: every question answered right");
          return r.result;
        } catch (e) {
          toast(`Could not mark it: ${msg(e)}`, true);
          return null;
        }
      },
      onNext: () => {
        i++;
        show();
        stage.scrollTop = 0;
        stage.scrollIntoView({ block: "nearest", behavior: "smooth" });
      },
    });
    stage.replaceChildren(card.el);
  };

  clear(root);
  append(root, [
    h(
      "div",
      { class: "headrow" },
      h("div", null, h("a", { class: "lbl", href: back, onclick: go(back) }, "← overview"), h("h1", null, title)),
    ),
    h(
      "div",
      { class: notesHTML ? "quiz-split" : "quiz-solo" },
      // Beside the question the notes stay open; stacked above it (a phone, a
      // narrow window) they start folded so the question is on screen.
      notesHTML
        ? h("details", { class: "panel notes", open: window.matchMedia("(min-width: 1180px)").matches }, h("summary", { class: "phead" }, h("h2", null, "Study notes")), html("div", "prose pbody", notesHTML))
        : null,
      questions.length ? stage : h("div", { class: "empty" }, h("h2", null, reviewing ? "Nothing to review" : "No questions yet"), h("p", null, reviewing ? "Every mistake has been cleared." : "")),
    ),
  ]);
  if (questions.length) show();
  return { dispose: () => card?.dispose() };
}

// ---------- a timed mock exam ----------

export async function quizExamPage(shell: Shell, track: string, exam: string): Promise<Page> {
  shell.setActive("misc");
  shell.setFill(false);
  const root = shell.content;
  clear(root);

  let overview: QuizOverview;
  try {
    overview = await api.quiz(track);
  } catch (e) {
    failPage(root, "Could not load the quiz", e);
    return {};
  }
  const found = overview.exams.find((x) => x.id === exam);
  if (!found) {
    failPage(root, "No such exam", exam);
    return {};
  }
  let spec = found;
  const back = `/quiz/${track}`;
  let timer = 0;
  let disposeKeys = () => {};
  const dispose = () => {
    clearInterval(timer);
    disposeKeys();
  };

  const intro = () => {
    const running = spec.deadline && new Date(spec.deadline).getTime() > Date.now();
    root.replaceChildren(
      h("div", { class: "headrow" }, h("div", null, h("a", { class: "lbl", href: back, onclick: go(back) }, "← overview"), h("h1", null, spec.title))),
      h(
        "section",
        { class: "q-card panel solo" },
        h(
          "div",
          { class: "q-body" },
          h("p", null, `${spec.tf} true/false questions${spec.scenarios ? ` and ${spec.scenarios} scenario questions` : ""}, ${spec.minutes} minutes.`),
          h(
            "p",
            null,
            `Each true/false question is worth ${spec.tf_points} point${spec.tf_points === 1 ? "" : "s"}`,
            spec.scenarios ? `; each scenario ${spec.scenario_points}, and only if all three of its statements are right` : "",
            `. Pass at ${spec.pass} of ${spec.max}.`,
          ),
          h("p", { class: "sub" }, "No feedback until you submit. The clock keeps running if you leave the page, and the exam submits itself when time runs out. Over time is a fail, as in the real test."),
          h("div", { class: "q-next" }, h("button", { class: "btn primary", onclick: () => void begin() }, running ? "Resume" : "Start the clock")),
        ),
      ),
    );
  };

  const begin = async () => {
    let s: ExamStart;
    try {
      s = await api.examStart(track, exam);
    } catch (e) {
      toast(msg(e), true);
      return;
    }
    run(s);
  };

  const run = (s: ExamStart) => {
    // The server's clock decides; this is only the offset to show it here.
    const skew = new Date(s.now).getTime() - Date.now();
    const deadline = new Date(s.deadline).getTime();
    const left = () => (deadline - (Date.now() + skew)) / 1000;
    // Answers live in the browser until submit, kept per exam so a reload of
    // a running exam does not lose them.
    const saveKey = `learnbox.exam.${track}.${exam}.${s.started}`;
    let answers: Record<string, QuizGiven> = {};
    try {
      answers = JSON.parse(sessionStorage.getItem(saveKey) ?? "{}");
    } catch {
      /* storage blocked */
    }
    const persist = () => {
      try {
        sessionStorage.setItem(saveKey, JSON.stringify(answers));
      } catch {
        /* storage blocked */
      }
    };
    const qs = s.questions;
    let at = 0;
    let submitting = false;

    const clock = h("span", { class: "exam-clock num" });
    const count = h("span", { class: "lbl" });
    const grid = h("div", { class: "exam-grid" });
    const stage = h("div");

    const isAnswered = (q: QuizQuestion) => {
      const a = answers[q.id];
      return q.kind === "scenario" ? (a?.answers ?? []).filter((x) => x !== undefined && x !== null).length === 3 : a?.answer !== undefined;
    };

    const paintGrid = () => {
      clear(grid);
      qs.forEach((q, k) =>
        grid.append(
          h(
            "button",
            {
              class: `cell${k === at ? " at" : ""}${isAnswered(q) ? " done" : ""}${q.kind === "scenario" ? " sc" : ""}`,
              title: q.kind === "scenario" ? `Scenario ${k + 1}` : `Question ${k + 1}`,
              onclick: () => {
                at = k;
                show();
              },
            },
            String(k + 1),
          ),
        ),
      );
      count.textContent = `${qs.filter(isAnswered).length} of ${qs.length} answered`;
      // On a phone the grid is one scrolling row: keep the current number in
      // the middle of it. (Wider, the row does not scroll and this is a no-op.)
      const cur = grid.querySelector<HTMLElement>(".at");
      if (cur) grid.scrollLeft = cur.offsetLeft - (grid.clientWidth - cur.offsetWidth) / 2;
    };

    const show = () => {
      const q = qs[at];
      const a = answers[q.id] ?? {};
      const body = h("div", { class: "q-body" }, questionText(q));
      if (q.kind === "scenario") {
        const picks = a.answers ?? [];
        (q.statements ?? []).forEach((st, i) =>
          body.append(
            h(
              "div",
              { class: "stmt" },
              h("span", { class: "stmt-n" }, String(i + 1)),
              questionText(st, "q-text small"),
              tfButtons((v) => {
                const next = [...(answers[q.id]?.answers ?? [])];
                next[i] = v;
                answers[q.id] = { answers: next };
                persist();
                show();
              }, picks[i]),
            ),
          ),
        );
      } else {
        body.append(
          tfButtons((v) => {
            answers[q.id] = { answer: v };
            persist();
            if (at < qs.length - 1) at++;
            show();
          }, a.answer),
        );
      }
      stage.replaceChildren(
        h(
          "section",
          { class: "q-card panel" },
          h("div", { class: "q-head" }, h("span", { class: "lbl" }, `${q.kind === "scenario" ? "Scenario" : "Question"} ${at + 1} of ${qs.length}`)),
          body,
          h(
            "div",
            { class: "q-next pad" },
            h("button", { class: "btn", disabled: at === 0, onclick: () => ((at = Math.max(0, at - 1)), show()) }, "Previous"),
            h("button", { class: "btn", disabled: at === qs.length - 1, onclick: () => ((at = Math.min(qs.length - 1, at + 1)), show()) }, "Next"),
          ),
        ),
      );
      paintGrid();
    };

    const submit = async (auto: boolean) => {
      if (submitting) return;
      const missing = qs.filter((q) => !isAnswered(q)).length;
      if (!auto && missing && !confirm(`${missing} question${missing === 1 ? " is" : "s are"} unanswered and will count as wrong. Submit now?`)) return;
      submitting = true;
      clearInterval(timer);
      try {
        const r = await api.examSubmit(track, exam, answers);
        try {
          sessionStorage.removeItem(saveKey);
        } catch {
          /* storage blocked */
        }
        shell.invalidateTracks();
        results(r.result, r.review);
      } catch (e) {
        submitting = false;
        toast(`Submit failed: ${msg(e)}`, true);
      }
    };

    const tick = () => {
      const l = left();
      clock.textContent = mmss(l);
      clock.classList.toggle("low", l < 120);
      if (l <= 0) void submit(true);
    };

    const keys = (e: KeyboardEvent) => {
      const q = qs[at];
      if (q.kind === "scenario" || (e.target as HTMLElement).closest("input, textarea")) return;
      const pick = e.key === "o" || e.key === "O" || e.key === "1" ? true : e.key === "x" || e.key === "X" || e.key === "2" ? false : undefined;
      if (pick !== undefined) {
        answers[q.id] = { answer: pick };
        persist();
        if (at < qs.length - 1) at++;
        show();
      } else if (e.key === "ArrowRight" && at < qs.length - 1) {
        at++;
        show();
      } else if (e.key === "ArrowLeft" && at > 0) {
        at--;
        show();
      }
    };
    document.addEventListener("keydown", keys);
    disposeKeys = () => document.removeEventListener("keydown", keys);

    root.replaceChildren(
      h(
        "div",
        { class: "exam-bar panel" },
        h("div", null, h("h1", { style: "font-size:18px;margin:0" }, spec.title), count),
        clock,
        h(
          "div",
          { style: "display:flex;gap:8px" },
          h(
            "button",
            {
              class: "btn ghost",
              onclick: async () => {
                if (!confirm("Abandon this exam? It will not be scored.")) return;
                dispose();
                await api.examAbandon(track, exam).catch(() => null);
                navigate(back);
              },
            },
            "Abandon",
          ),
          h("button", { class: "btn primary", onclick: () => void submit(false) }, "Submit"),
        ),
      ),
      h("div", { class: "exam-split" }, stage, h("aside", { class: "panel exam-side" }, h("div", { class: "phead" }, h("h2", null, "Questions")), grid)),
    );
    show();
    tick();
    timer = window.setInterval(tick, 500);
  };

  const results = (r: ExamResult, review: QuizExplanation[]) => {
    dispose();
    const wrong = review.filter((x) => !x.correct);
    clear(root);
    append(root, [
      h("div", { class: "headrow" }, h("div", null, h("a", { class: "lbl", href: back, onclick: go(back) }, "← overview"), h("h1", null, spec.title))),
      h(
        "section",
        { class: `panel exam-result ${r.passed ? "pass" : "fail"}` },
        h("p", { class: "big num" }, `${r.score} / ${r.max}`),
        h("p", { class: "verdict" }, r.passed ? "PASS" : "FAIL"),
        h("p", { class: "sub" }, `${mmss(r.seconds)} used of ${spec.minutes}:00${r.overtime ? " - over time, which fails however high the score" : ""} · pass mark ${spec.pass}`),
        h(
          "div",
          { class: "q-next", style: "justify-content:center" },
          h("a", { class: "btn primary", href: `/quiz/${track}/exam/${exam}`, onclick: (e: Event) => (e.preventDefault(), void render()) }, "Another mock exam"),
          wrong.length ? h("a", { class: "btn am", href: `/quiz/${track}/mistakes`, onclick: go(`/quiz/${track}/mistakes`) }, "Review mistakes") : null,
        ),
      ),
      wrong.length
        ? h(
            "section",
            { class: "panel", style: "margin-top:18px" },
            h("div", { class: "phead" }, h("h2", null, `${wrong.length} to learn from`)),
            ...wrong.map((x) => h("div", { class: "review-item" }, x.question ? questionText(x.question) : null, feedback(x))),
          )
        : null,
    ]);
  };

  const render = async () => {
    try {
      overview = await api.quiz(track);
      spec = overview.exams.find((x) => x.id === exam) ?? spec;
    } catch {
      /* keep the old one */
    }
    intro();
  };

  intro();
  return { dispose };
}
