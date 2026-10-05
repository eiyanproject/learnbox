import { api, type Badge, type Reward, type Standing } from "./api";
import { h, icon } from "./dom";
import { icons } from "./icons";

// The learner's XP and level, shared by the top bar and whatever page changes
// them. A check returns the new standing with its reward, so nothing polls.

let current: Standing | null = null;
const listeners = new Set<(s: Standing) => void>();

export function onStanding(fn: (s: Standing) => void) {
  listeners.add(fn);
  if (current) fn(current);
}

export function setStanding(s: Standing) {
  current = s;
  for (const fn of listeners) fn(s);
}

export async function refreshStanding() {
  try {
    setStanding(await api.summary());
  } catch {
    /* no profile picked yet, or the server is away; the next check will say */
  }
}

/** Share of the current level done, 0-100. */
export function levelPct(s: Standing): number {
  const span = s.next_level - s.level_floor;
  return span > 0 ? Math.min(100, Math.round(((s.xp - s.level_floor) / span) * 100)) : 0;
}

export const xpText = (n: number) => `${n.toLocaleString("en-US")} XP`;

// ---------- reward cards ----------

let stack: HTMLElement | null = null;

function card(cls: string, glyph: HTMLElement, title: string, text: string, ms: number) {
  if (!stack || !stack.isConnected) {
    stack = h("div", { class: "rewards", role: "status", "aria-live": "polite" });
    document.body.append(stack);
  }
  const el = h("button", { class: `reward ${cls}`, type: "button", title: "Dismiss" }, h("span", { class: "reward-mark" }, glyph), h("span", { class: "reward-text" }, h("b", null, title), h("span", null, text)));
  const close = () => el.remove();
  el.addEventListener("click", close);
  stack.append(el);
  window.setTimeout(close, ms);
}

export function badgeGlyph(b: Pick<Badge, "family">): HTMLElement {
  return icon(b.family === "secret" ? icons.key : b.family === "calendar" ? icons.flame : b.family === "style" ? icons.star : b.family === "completion" ? icons.flag : icons.medal);
}

/** Announces what a check earned and moves the top bar along. */
export function showReward(r: Reward) {
  setStanding(r.standing);
  if (r.xp > 0) card("xp", icon(icons.bolt), `+${xpText(r.xp)}`, `${xpText(r.standing.xp)} in total`, 5000);
  if (r.level_up) card("level", icon(icons.up), `Level ${r.standing.level}`, r.standing.title, 8000);
  for (const b of r.badges) card("badge-won", badgeGlyph(b), b.name, b.description, 9000);
}
