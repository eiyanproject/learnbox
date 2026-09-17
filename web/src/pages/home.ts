import { api, type ServerStatus, type Track, type TracksResponse } from "../api";
import { clear, h } from "../dom";
import { navigate, type Page } from "../router";
import type { Shell } from "../shell";

const pct = (a: number, b: number) => (b ? Math.round((a / b) * 100) : 0);

function link(href: string, cls: string, ...children: (Node | string | null)[]) {
  return h("a", { href, class: cls, onclick: (e: Event) => (e.preventDefault(), navigate(href)) }, ...children);
}

function kpi(label: string, value: string, sub = "", bars = [5, 9, 6, 13]) {
  return h(
    "div",
    { class: "kpi" },
    h(
      "div",
      { class: "kpi-head" },
      h("span", { class: "lbl" }, label),
      h("span", { class: "tick" }, ...bars.map((b) => h("i", { style: `height:${b}px` }))),
    ),
    h("span", { class: "n" }, value, sub ? h("small", null, sub) : null),
  );
}

function trackCard(t: Track) {
  return link(
    `/track/${t.lang}`,
    "track-card",
    h(
      "div",
      null,
      h("h3", null, t.title),
      h("p", null, t.description),
      h(
        "div",
        { class: "secbars" },
        ...t.sections.map((s) =>
          h(
            "div",
            { class: "secbar" },
            h(
              "div",
              { class: "top-line" },
              h("span", { class: "lbl" }, s.title),
              h("span", { class: "lbl" }, `${s.passed} / ${s.lessons.length}`),
            ),
            h("span", { class: "meter" }, h("i", { style: `width:${pct(s.passed, s.lessons.length)}%` })),
          ),
        ),
      ),
    ),
    h("span", { class: "num", style: "font-size:22px;font-weight:600" }, `${pct(t.passed, t.total)}%`),
  );
}

export async function homePage(shell: Shell): Promise<Page> {
  shell.setActive("home");
  shell.setFill(false);
  const root = shell.content;
  clear(root);
  root.append(h("div", { class: "skel" }), h("div", { class: "skel", style: "height:260px" }));

  let data: TracksResponse;
  let status: ServerStatus | null = null;
  try {
    [data, status] = await Promise.all([api.tracks(), api.status().catch(() => null)]);
  } catch (e) {
    clear(root);
    root.append(h("div", { class: "empty" }, h("h2", null, "Cannot reach the server"), h("p", null, String(e))));
    return {};
  }

  const passed = data.tracks.reduce((n, t) => n + t.passed, 0);
  const total = data.tracks.reduce((n, t) => n + t.total, 0);
  const byLang = (lang: string) => data.tracks.find((t) => t.lang === lang);
  const py = byLang("python");
  const rs = byLang("rust");

  clear(root);
  root.append(
    h(
      "div",
      { class: "headrow" },
      h(
        "div",
        null,
        h("h1", null, "Learning terminal"),
        h("p", { class: "sub" }, "Read a lesson, write the code, run it in a real shell. Every check runs on this machine."),
      ),
      data.last_lesson
        ? link(`/learn/${data.last_lesson.id}`, "btn primary", `Resume: ${data.last_lesson.title}`)
        : py
          ? link(`/learn/${py.sections[0]?.lessons[0]?.id ?? ""}`, "btn primary", "Start with Python")
          : null,
    ),
    h(
      "div",
      { class: "kpis" },
      kpi("Passed", String(passed), `/ ${total}`),
      kpi("Python", py ? `${pct(py.passed, py.total)}%` : "—", py ? `${py.passed} done` : "", [4, 7, 11, 9]),
      kpi("Rust", rs ? `${pct(rs.passed, rs.total)}%` : "—", rs ? `${rs.passed} done` : "", [9, 5, 12, 7]),
      kpi("Shells", status ? String(status.sessions) : "—", "live", [3, 6, 4, 8]),
    ),
    h(
      "div",
      { class: "body" },
      h(
        "section",
        { class: "panel" },
        h("div", { class: "phead" }, h("h2", null, "Tracks"), h("span", { class: "lbl" }, `${total} lessons`)),
        ...data.tracks.map(trackCard),
      ),
      h(
        "aside",
        { class: "panel" },
        h("div", { class: "phead" }, h("h2", null, "Machine"), h("span", { class: "lbl" }, status ? `v${status.version}` : "")),
        h(
          "div",
          { class: "pbody" },
          kv("Python", status?.tools.python || "not installed"),
          kv("Rust", status?.tools.rust || "not installed"),
          kv("Resource limits", status ? (status.limits_active ? "on" : "off") : "?", !status?.limits_active),
          kv("Workspace", "~/learn"),
          h(
            "p",
            { class: "sub", style: "margin-top:12px;font-size:12px" },
            "Files you edit live in the learner's home directory. The terminal and the editor see the same files.",
          ),
        ),
      ),
    ),
  );
  return {};
}

function kv(k: string, v: string, off = false) {
  return h("div", { class: "kv" }, h("span", null, k), h("span", { class: off ? "v off" : "v" }, v));
}
