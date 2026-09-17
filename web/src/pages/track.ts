import { api, type LessonSummary, type Track } from "../api";
import { clear, h } from "../dom";
import { navigate, type Page } from "../router";
import type { Shell } from "../shell";
import { store, stored } from "../theme";

type Filter = "all" | "todo" | "passed";

function statusBadge(s: LessonSummary["status"]) {
  if (s === "passed") return h("span", { class: "badge passed" }, "passed");
  if (s === "started") return h("span", { class: "badge started" }, "started");
  return h("span", { class: "badge" }, "new");
}

function difficulty(n?: number) {
  if (!n) return h("span", { class: "lbl" }, "guided");
  const filled = Math.max(1, Math.min(5, Math.ceil(n / 2)));
  return h("span", { class: "diff", title: `difficulty ${n}/10` }, ...[1, 2, 3, 4, 5].map((i) => h("i", { class: i <= filled ? "f" : "" })));
}

export async function trackPage(shell: Shell, lang: string): Promise<Page> {
  shell.setActive(lang);
  shell.setFill(false);
  const root = shell.content;
  clear(root);
  root.append(h("div", { class: "skel" }), h("div", { class: "skel", style: "height:400px" }));

  let track: Track | undefined;
  try {
    track = (await api.tracks()).tracks.find((t) => t.lang === lang);
  } catch (e) {
    clear(root);
    root.append(h("div", { class: "empty" }, h("h2", null, "Cannot reach the server"), h("p", null, String(e))));
    return {};
  }
  if (!track) {
    clear(root);
    root.append(h("div", { class: "empty" }, h("h2", null, "No such track"), h("p", null, `Nothing is installed for "${lang}".`)));
    return {};
  }
  const t = track;

  let section = stored<string>(`track.${lang}.section`, t.sections[0]?.id ?? "");
  if (!t.sections.some((s) => s.id === section)) section = t.sections[0]?.id ?? "";
  let filter = stored<Filter>(`track.${lang}.filter`, "all");

  const head = h("div", { class: "headrow" });
  const list = h("section", { class: "panel" });
  root.replaceChildren(head, list);

  const draw = () => {
    const sec = t.sections.find((s) => s.id === section);
    if (!sec) return;

    head.replaceChildren(
      h("div", null, h("span", { class: "lbl" }, `Track · ${t.passed} of ${t.total} passed`), h("h1", null, t.title), h("p", { class: "sub" }, t.description)),
      h(
        "div",
        { class: "seg" },
        ...t.sections.map((s) =>
          h(
            "button",
            {
              class: s.id === section ? "on" : "",
              onclick: () => {
                section = s.id;
                store(`track.${lang}.section`, section);
                draw();
              },
            },
            `${s.title} ${s.lessons.length}`,
          ),
        ),
      ),
    );

    const lessons = sec.lessons.filter((l) => (filter === "all" ? true : filter === "passed" ? l.status === "passed" : l.status !== "passed"));
    const firstTodo = sec.lessons.find((l) => l.status !== "passed");

    list.replaceChildren(
      h(
        "div",
        { class: "phead" },
        h("div", null, h("h2", null, sec.title), h("span", { class: "lbl" }, sec.description)),
        h(
          "div",
          { class: "chips" },
          ...(["all", "todo", "passed"] as Filter[]).map((f) =>
            h(
              "button",
              {
                class: f === filter ? "chip on" : "chip",
                onclick: () => {
                  filter = f;
                  store(`track.${lang}.filter`, f);
                  draw();
                },
              },
              f,
            ),
          ),
          firstTodo
            ? h("a", { class: "btn primary", href: `/learn/${firstTodo.id}`, onclick: (e: Event) => (e.preventDefault(), navigate(`/learn/${firstTodo.id}`)) }, "Next up")
            : null,
        ),
      ),
      h(
        "div",
        { class: "rowhead" },
        h("span", { class: "lbl" }, "#"),
        h("span", { class: "lbl" }, "Lesson"),
        h("span", { class: "lbl hide-sm" }, "Level"),
        h("span", { class: "lbl right" }, "Status"),
      ),
      ...(lessons.length
        ? lessons.map((l) => {
            const idx = sec.lessons.indexOf(l) + 1;
            return h(
              "a",
              { class: "row", href: `/learn/${l.id}`, onclick: (e: Event) => (e.preventDefault(), navigate(`/learn/${l.id}`)) },
              h("span", { class: "idx" }, String(idx).padStart(2, "0")),
              h("div", { style: "min-width:0" }, h("p", { class: "rt" }, l.title), h("p", { class: "rd" }, l.summary)),
              h("span", { class: "hide-sm" }, difficulty(l.difficulty)),
              h("span", { class: "right" }, statusBadge(l.status)),
            );
          })
        : [
            h(
              "div",
              { class: "empty" },
              h("h2", null, sec.lessons.length ? "Nothing here" : "No lessons yet"),
              h(
                "p",
                null,
                sec.lessons.length
                  ? "Try another filter."
                  : sec.id === "practice"
                    ? "Practice exercises are imported from Exercism by the install script."
                    : "",
              ),
            ),
          ]),
    );
  };
  draw();
  return {};
}
