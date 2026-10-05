import { api, ApiError, type ArenaResponse, type ChallengeView, type Ladder } from "../api";
import { clear, h, icon, toast } from "../dom";
import { xpText } from "../game";
import { icons } from "../icons";
import { navigate, type Page } from "../router";
import type { Shell } from "../shell";

/** mm:ss until a server time, given how far this clock is from the server's. */
export function clock(untilIso: string, skewMs: number): { text: string; ms: number } {
  const ms = Math.max(0, new Date(untilIso).getTime() - (Date.now() + skewMs));
  const s = Math.ceil(ms / 1000);
  return { text: `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`, ms };
}

const duration = (secs: number) => (secs >= 60 ? `${Math.floor(secs / 60)}m ${secs % 60}s` : `${secs}s`);

export async function arenaPage(shell: Shell): Promise<Page> {
  shell.setActive("arena");
  shell.setFill(false);
  const root = shell.content;
  clear(root);
  root.append(h("div", { class: "skel" }), h("div", { class: "skel", style: "height:400px" }));

  let disposed = false;
  let timer = 0;
  let tickers: (() => void)[] = [];

  const start = async (c: ChallengeView) => {
    const again = c.wins > 0 ? " You have won it before; only a better result counts." : "";
    if (!confirm(`Start "${c.title}"?\n\nYou have ${c.minutes} minutes, and the clock starts now. Run out of time and the attempt is lost, with a ${c.cooldown_minutes} minute cooldown before the next.${again}\n\nThe files are reset to the starter.`)) return;
    try {
      await api.startChallenge(c.id);
      navigate(`/learn/${c.id}`);
    } catch (e) {
      toast(e instanceof Error ? e.message : String(e), true);
      void load();
    }
  };

  const card = (c: ChallengeView, n: number, skew: number) => {
    const action = h("div", { class: "ch-act" });
    const state = h("span", { class: "badge" });
    switch (c.state) {
      case "active": {
        state.className = "badge started";
        const btn = h("button", { class: "btn primary", onclick: () => navigate(`/learn/${c.id}`) }, "Resume");
        const left = h("span", { class: "num ch-clock" });
        tickers.push(() => {
          const t = clock(c.deadline!, skew);
          left.textContent = t.text;
          state.textContent = "running";
          if (t.ms === 0) void load();
        });
        action.append(left, btn);
        break;
      }
      case "cooldown": {
        state.className = "badge failed";
        const left = h("span", { class: "num ch-clock" });
        tickers.push(() => {
          const t = clock(c.cooldown_until!, skew);
          left.textContent = t.text;
          state.textContent = "cooling down";
          if (t.ms === 0) void load();
        });
        action.append(left, h("button", { class: "btn", disabled: true }, "Wait"));
        break;
      }
      case "locked":
        state.textContent = "locked";
        action.append(h("button", { class: "btn", disabled: true }, "Locked"));
        break;
      case "won":
        state.className = "badge passed";
        state.textContent = "won";
        action.append(
          h("button", { class: "btn ghost", onclick: () => navigate(`/learn/${c.id}`) }, "Open"),
          h("button", { class: "btn", onclick: () => void start(c) }, "Go again"),
        );
        break;
      default:
        state.className = "badge started";
        state.textContent = "ready";
        action.append(h("button", { class: "btn primary", onclick: () => void start(c) }, icon(icons.play), `Start · ${c.minutes} min`));
    }

    const record: string[] = [];
    if (c.wins) record.push(`best ${duration(c.best_seconds ?? 0)} · ${xpText(c.best_xp ?? 0)}`);
    if (c.losses) record.push(`${c.losses} lost`);

    return h(
      "div",
      { class: `ch ${c.state}${c.boss ? " boss" : ""}` },
      h("span", { class: "idx" }, c.boss ? "BOSS" : String(n).padStart(2, "0")),
      h(
        "div",
        { class: "ch-body" },
        h("p", { class: "rt" }, c.title),
        h("p", { class: "rd" }, c.summary),
        h("span", { class: "lbl" }, `${c.minutes} min · ${c.xp} to ${c.max_xp} XP${record.length ? " · " + record.join(" · ") : ""}`),
        c.locks.length ? h("ul", { class: "ch-locks" }, ...c.locks.map((l) => h("li", null, l))) : null,
      ),
      state,
      action,
    );
  };

  const ladder = (l: Ladder, skew: number) => {
    const won = l.challenges.filter((c) => c.wins > 0).length;
    return h(
      "section",
      { class: "panel" },
      h(
        "div",
        { class: "phead" },
        h("div", null, h("h2", null, l.title), h("span", { class: "lbl" }, `${xpText(l.track_xp)} earned in this track`)),
        h("span", { class: "lbl" }, `${won} / ${l.challenges.length} won`),
      ),
      ...l.challenges.map((c, i) => card(c, i + 1, skew)),
    );
  };

  const draw = (data: ArenaResponse) => {
    const skew = new Date(data.now).getTime() - Date.now();
    tickers = [];
    clear(root);
    root.append(
      h(
        "div",
        { class: "headrow" },
        h(
          "div",
          null,
          h("span", { class: "lbl" }, "Timed challenges"),
          h("h1", null, "Arena"),
          h(
            "p",
            { class: "sub" },
            "Each track has a ladder: rounds, then a boss. Starting a challenge starts its clock. Pass every test in time and you win its XP, with up to half as much again for speed. Run out of time and the attempt is lost.",
          ),
        ),
      ),
      ...(data.ladders.length
        ? data.ladders.map((l) => ladder(l, skew))
        : [h("div", { class: "empty" }, h("h2", null, "No challenges yet"), h("p", null, "No track has an arena section installed."))]),
    );
    for (const t of tickers) t();
  };

  const load = async () => {
    if (disposed) return;
    try {
      const data = await api.arena();
      if (!disposed) draw(data);
    } catch (e) {
      if (disposed) return;
      clear(root);
      root.append(h("div", { class: "empty" }, h("h2", null, "Cannot load the arena"), h("p", null, e instanceof ApiError ? e.message : String(e))));
    }
  };

  await load();
  timer = window.setInterval(() => {
    for (const t of tickers) t();
  }, 500);

  return {
    dispose: () => {
      disposed = true;
      clearInterval(timer);
    },
  };
}
