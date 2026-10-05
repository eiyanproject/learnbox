import { api, type Badge, type BadgeFamily, type Summary } from "../api";
import { clear, h } from "../dom";
import { badgeGlyph, levelPct, setStanding, xpText } from "../game";
import { navigate, type Page } from "../router";
import type { Shell } from "../shell";

const families: { id: BadgeFamily; title: string; note: string }[] = [
  { id: "milestone", title: "Milestones", note: "How far you have come" },
  { id: "completion", title: "Completion", note: "Sections and tracks finished" },
  { id: "style", title: "Style", note: "How you got there" },
  { id: "calendar", title: "Calendar", note: "When you showed up" },
  { id: "secret", title: "Secret", note: "Find out by doing" },
];

const pct = (a: number, b: number) => (b ? Math.min(100, Math.round((a / b) * 100)) : 0);

function day(iso?: string) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function tile(b: Badge) {
  return h(
    "div",
    { class: b.earned ? "btile on" : "btile" },
    h("span", { class: "btile-mark" }, badgeGlyph(b)),
    h(
      "div",
      { class: "btile-body" },
      h("p", { class: "rt" }, b.name),
      h("p", { class: "rd" }, b.description),
      b.earned
        ? h("span", { class: "lbl" }, `earned ${day(b.earned_at)}`)
        : b.want > 1
          ? h("div", { class: "btile-prog" }, h("span", { class: "meter cy" }, h("i", { style: `width:${pct(b.have, b.want)}%` })), h("span", { class: "lbl" }, `${b.have} / ${b.want}`))
          : h("span", { class: "lbl" }, "locked"),
    ),
  );
}

function kpi(label: string, value: string, sub = "") {
  return h("div", { class: "kpi" }, h("div", { class: "kpi-head" }, h("span", { class: "lbl" }, label)), h("span", { class: "n" }, value, sub ? h("small", null, sub) : null));
}

export async function badgesPage(shell: Shell): Promise<Page> {
  shell.setActive("badges");
  shell.setFill(false);
  const root = shell.content;
  clear(root);
  root.append(h("div", { class: "skel" }), h("div", { class: "skel", style: "height:400px" }));

  let s: Summary;
  try {
    s = await api.summary();
  } catch (e) {
    clear(root);
    root.append(h("div", { class: "empty" }, h("h2", null, "Cannot load your badges"), h("p", null, String(e instanceof Error ? e.message : e))));
    return {};
  }
  setStanding(s);

  const earned = s.badges.filter((b) => b.earned).length;
  clear(root);
  root.append(
    h(
      "div",
      { class: "headrow" },
      h(
        "div",
        null,
        h("span", { class: "lbl" }, `Level ${s.level} · ${s.title}`),
        h("h1", null, "Badges"),
        h("p", { class: "sub" }, "Passing a lesson pays XP; each hint you reveal first takes 10% off, down to half. Badges are for the how and the when."),
      ),
    ),
    h(
      "div",
      { class: "kpis" },
      kpi("Level", String(s.level), s.title),
      kpi("XP", s.xp.toLocaleString("en-US")),
      kpi("Badges", String(earned), `/ ${s.badges.length}`),
      kpi("Passed", String(s.passed), "lessons"),
    ),
    h(
      "section",
      { class: "panel" },
      h("div", { class: "phead" }, h("h2", null, `Level ${s.level + 1} at ${xpText(s.next_level)}`), h("span", { class: "lbl" }, `${xpText(s.next_level - s.xp)} to go`)),
      h("div", { class: "pbody" }, h("span", { class: "meter cy tall" }, h("i", { style: `width:${levelPct(s)}%` }))),
    ),
    h(
      "div",
      { class: "body" },
      h(
        "div",
        { class: "bfams" },
        ...families.map((f) => {
          const list = s.badges.filter((b) => b.family === f.id);
          return h(
            "section",
            { class: "panel" },
            h("div", { class: "phead" }, h("div", null, h("h2", null, f.title), h("span", { class: "lbl" }, f.note)), h("span", { class: "lbl" }, `${list.filter((b) => b.earned).length} / ${list.length}`)),
            h("div", { class: "bgrid" }, ...list.map(tile)),
          );
        }),
      ),
      h(
        "aside",
        { class: "panel" },
        h("div", { class: "phead" }, h("h2", null, "XP by track"), h("span", { class: "lbl" }, xpText(s.xp))),
        h(
          "div",
          { class: "pbody" },
          ...s.tracks
            .filter((t) => t.possible > 0)
            .map((t) =>
              h(
                "a",
                { class: "secbar", href: `/track/${t.lang}`, onclick: (e: Event) => (e.preventDefault(), navigate(`/track/${t.lang}`)) },
                h("div", { class: "top-line" }, h("span", { class: "lbl" }, t.title), h("span", { class: "lbl" }, `${t.xp.toLocaleString("en-US")} / ${t.possible.toLocaleString("en-US")}`)),
                h("span", { class: "meter" }, h("i", { style: `width:${pct(t.xp, t.possible)}%` })),
              ),
            ),
        ),
      ),
    ),
  );
  return {};
}
