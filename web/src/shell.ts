import { api, type ServerStatus, type TracksResponse } from "./api";
import { clear, h, icon } from "./dom";
import { icons } from "./icons";
import { navigate } from "./router";
import { onTheme, theme, toggleTheme } from "./theme";

/** Rail + top bar around every page. Pages render into `content`. */
export class Shell {
  readonly content: HTMLElement;
  private navItems = new Map<string, HTMLElement>();
  private statusEl: HTMLElement;
  private themeBtn: HTMLButtonElement;
  private themeIcon: HTMLElement;
  private tracks: TracksResponse | null = null;

  constructor(root: HTMLElement) {
    const nav = (key: string, title: string, href: string, glyph: HTMLElement | string) => {
      const el = h(
        "a",
        {
          class: "nav",
          href,
          title,
          "aria-label": title,
          onclick: (e: Event) => {
            e.preventDefault();
            navigate(href);
          },
        },
        typeof glyph === "string" ? h("span", { class: "glyph" }, glyph) : glyph,
      );
      this.navItems.set(key, el);
      return el;
    };

    this.themeIcon = h("span", { style: "display:contents" });
    const railTheme = h("button", { class: "nav", title: "Toggle theme", "aria-label": "Toggle theme", onclick: () => toggleTheme() }, this.themeIcon);

    const rail = h(
      "aside",
      { class: "rail" },
      h("a", { class: "mark", href: "/", title: "learnbox", onclick: (e: Event) => (e.preventDefault(), navigate("/")) }, icon(icons.mark)),
      nav("home", "Overview", "/", icon(icons.home)),
      nav("python", "Python", "/track/python", "py"),
      nav("rust", "Rust", "/track/rust", "rs"),
      nav("terminal", "Terminal", "/terminal", icon(icons.terminal)),
      h("div", { class: "spacer" }),
      railTheme,
    );

    this.statusEl = h("div", { class: "status" }, h("span", { class: "dot off" }), h("span", null, "CONNECTING"));
    this.themeBtn = h("button", { class: "tog", onclick: () => toggleTheme() });
    this.content = h("main", { class: "content" });

    const top = h("header", { class: "top" }, this.jumpBox(), this.statusEl, this.themeBtn);
    root.append(h("div", { class: "shell" }, rail, h("div", { class: "col" }, top, this.content)));

    const paintTheme = () => {
      this.themeBtn.textContent = theme() === "dark" ? "Dark" : "Light";
      clear(this.themeIcon);
      this.themeIcon.append(icon(theme() === "dark" ? icons.sun : icons.moon));
    };
    paintTheme();
    onTheme(paintTheme);

    this.refreshStatus();
    setInterval(() => this.refreshStatus(), 30000);
  }

  setActive(key: string) {
    for (const [k, el] of this.navItems) el.classList.toggle("on", k === key);
  }

  /** Page layout: scrolling (default) or fixed-height (lesson, terminal). */
  setFill(fill: boolean) {
    this.content.classList.toggle("fill", fill);
    this.content.scrollTop = 0;
  }

  invalidateTracks() {
    this.tracks = null;
  }

  private async refreshStatus() {
    let s: ServerStatus;
    try {
      s = await api.status();
    } catch {
      clear(this.statusEl);
      this.statusEl.append(h("span", { class: "dot off" }), h("span", null, "SERVER OFFLINE"));
      return;
    }
    const parts: (string | HTMLElement)[] = [h("span", { class: "dot" }), h("span", null, "PTY ONLINE")];
    const sep = () => h("span", { class: "sep" }, "·");
    parts.push(sep(), h("span", null, s.tools.python ? `PY ${s.tools.python}` : "NO PYTHON"));
    parts.push(sep(), h("span", null, s.tools.rust ? `RUSTC ${s.tools.rust}` : "NO RUST"));
    if (!s.limits_active) parts.push(sep(), h("span", { style: "color:var(--am)" }, "NO LIMITS"));
    clear(this.statusEl);
    this.statusEl.append(...parts);
  }

  /** The search pill: jump to any lesson by title. "/" focuses it. */
  private jumpBox(): HTMLElement {
    const input = h("input", { type: "search", placeholder: "Jump to a lesson", "aria-label": "Jump to a lesson", autocomplete: "off", spellcheck: "false" });
    const list = h("div", { class: "jump", hidden: true, role: "listbox" });
    let hi = 0;
    let results: { id: string; title: string; where: string; status: string }[] = [];

    const render = () => {
      clear(list);
      if (!results.length) {
        list.append(h("div", { class: "empty-row" }, "No lessons match"));
        return;
      }
      results.forEach((r, i) => {
        list.append(
          h(
            "a",
            {
              href: `/learn/${r.id}`,
              class: i === hi ? "hi" : "",
              onmousedown: (e: Event) => {
                e.preventDefault();
                go(r.id);
              },
            },
            h("span", { class: "lbl" }, r.where),
            h("span", null, r.title),
            r.status === "passed" ? h("span", { class: "badge passed" }, "passed") : null,
          ),
        );
      });
    };

    const search = async () => {
      const q = input.value.trim().toLowerCase();
      if (!q) {
        list.hidden = true;
        return;
      }
      if (!this.tracks) {
        try {
          this.tracks = await api.tracks();
        } catch {
          return;
        }
      }
      const all: typeof results = [];
      for (const t of this.tracks.tracks)
        for (const s of t.sections)
          for (const l of s.lessons)
            all.push({ id: l.id, title: l.title, where: `${t.lang === "python" ? "py" : t.lang === "rust" ? "rs" : t.lang} ${s.id}`, status: l.status });
      results = all.filter((r) => r.title.toLowerCase().includes(q) || r.id.includes(q)).slice(0, 30);
      hi = 0;
      list.hidden = false;
      render();
    };

    const go = (id: string) => {
      input.value = "";
      list.hidden = true;
      input.blur();
      navigate(`/learn/${id}`);
    };

    input.addEventListener("input", search);
    input.addEventListener("blur", () => setTimeout(() => (list.hidden = true), 100));
    input.addEventListener("keydown", (e) => {
      if (list.hidden) return;
      if (e.key === "ArrowDown") {
        hi = Math.min(results.length - 1, hi + 1);
        render();
        e.preventDefault();
      } else if (e.key === "ArrowUp") {
        hi = Math.max(0, hi - 1);
        render();
        e.preventDefault();
      } else if (e.key === "Enter" && results[hi]) {
        go(results[hi].id);
      } else if (e.key === "Escape") {
        input.value = "";
        list.hidden = true;
        input.blur();
      }
    });
    document.addEventListener("keydown", (e) => {
      const target = e.target as HTMLElement;
      const typing = target.closest("input, textarea, .cm-editor, .xterm");
      if (e.key === "/" && !typing) {
        e.preventDefault();
        input.focus();
      }
    });

    return h("label", { class: "pill" }, icon(icons.search), input, list, h("span", { class: "kbd" }, "/"));
  }
}
