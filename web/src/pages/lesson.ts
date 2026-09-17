import { api, ApiError, type CheckResponse, type Lesson } from "../api";
import { CodeEditor } from "../components/editor";
import { TermView } from "../components/terminal";
import { clear, h, html, icon, toast } from "../dom";
import { icons } from "../icons";
import { navigate, type Page } from "../router";
import type { Shell } from "../shell";
import { store, stored } from "../theme";

interface FileState {
  mtime: number;
  dirty: boolean;
  saving: Promise<void> | null;
  tab: HTMLButtonElement;
  dot: HTMLElement;
}

export async function lessonPage(shell: Shell, id: string): Promise<Page> {
  shell.setActive(id.split("/")[0]);
  shell.setFill(true);
  const root = shell.content;
  clear(root);
  root.append(h("div", { class: "skel", style: "height:44px" }), h("div", { class: "skel", style: "flex:1" }));

  let lesson: Lesson;
  try {
    lesson = await api.lesson(id);
  } catch (e) {
    clear(root);
    root.append(
      h(
        "div",
        { class: "empty" },
        h("h2", null, e instanceof ApiError && e.status === 404 ? "No such lesson" : "Could not load the lesson"),
        h("p", null, String(e instanceof Error ? e.message : e)),
      ),
    );
    return {};
  }
  return new LessonView(shell, lesson).page();
}

class LessonView {
  private editor!: CodeEditor;
  private term: TermView;
  private files = new Map<string, FileState>();
  private active = "";
  private saveTimer = 0;
  private pollTimer = 0;
  private disposed = false;

  private statusBadge = h("span", { class: "badge" });
  private saveState = h("span", { class: "save-state" }, "saved");
  private hintsBox = h("div", { class: "hints" });
  private resultsBox = h("div", { class: "results" });
  private resultsCount = h("span", { class: "count", hidden: true });
  private termTab!: HTMLButtonElement;
  private resultsTab!: HTMLButtonElement;
  private checkBtn!: HTMLButtonElement;

  constructor(
    private shell: Shell,
    private lesson: Lesson,
  ) {
    this.term = new TermView(`lesson/${lesson.id}`);
  }

  page(): Page {
    this.render();
    return {
      beforeLeave: () => {
        void this.flush();
        return true;
      },
      dispose: () => this.dispose(),
    };
  }

  private render() {
    const l = this.lesson;
    const root = this.shell.content;
    clear(root);
    this.paintStatus();

    // ---- header
    const go = (href: string) => (e: Event) => {
      e.preventDefault();
      navigate(href);
    };
    const head = h(
      "div",
      { class: "lesson-head" },
      h(
        "div",
        { class: "crumbs" },
        h(
          "span",
          { class: "lbl" },
          h("a", { href: `/track/${l.lang}`, onclick: go(`/track/${l.lang}`), style: "color:inherit" }, l.track_title),
          ` · ${l.section_title} · `,
          h("span", { style: "text-transform:none;letter-spacing:0.02em" }, l.workspace),
        ),
        h("h1", { title: l.title }, l.title),
      ),
      this.statusBadge,
      h(
        "div",
        { class: "nav-btns" },
        h("button", { class: "btn ghost", disabled: !l.prev, title: l.prev?.title ?? "", onclick: () => l.prev && navigate(`/learn/${l.prev.id}`) }, icon(icons.left), "Prev"),
        h("button", { class: "btn ghost", disabled: !l.next, title: l.next?.title ?? "", onclick: () => l.next && navigate(`/learn/${l.next.id}`) }, "Next", icon(icons.right)),
      ),
    );

    // ---- left: explanation
    const left = h(
      "section",
      { class: "pane" },
      h(
        "div",
        { class: "pane-scroll" },
        html("article", "prose", l.html),
        l.hints_total > 0 ? this.hintsBox : null,
        l.source_html ? html("div", "source", l.source_html) : null,
        h(
          "div",
          { class: "lesson-foot" },
          l.prev ? h("a", { class: "btn", href: `/learn/${l.prev.id}`, onclick: go(`/learn/${l.prev.id}`) }, icon(icons.left), l.prev.title) : h("span"),
          l.next ? h("a", { class: "btn", href: `/learn/${l.next.id}`, onclick: go(`/learn/${l.next.id}`) }, l.next.title, icon(icons.right)) : h("span"),
        ),
      ),
    );
    this.paintHints(l.hints);

    // ---- right: editor over terminal/results
    const fileTabs = h("div", { style: "display:flex;min-width:0;overflow-x:auto" });
    for (const name of l.files) {
      const dot = h("span", { class: "dirty", hidden: true });
      const tab = h("button", { class: "tab", onclick: () => this.showFile(name) }, name, dot);
      fileTabs.append(tab);
      this.files.set(name, { mtime: 0, dirty: false, saving: null, tab, dot });
    }

    const runBtn = l.run
      ? h("button", { class: "btn", title: `${l.run}  (Ctrl+Enter)`, onclick: () => this.run() }, icon(icons.play), "Run")
      : null;
    this.checkBtn = h(
      "button",
      { class: "btn primary", title: "Run the hidden tests  (Ctrl+Shift+Enter)", disabled: !l.has_tests, onclick: () => this.check() },
      icon(icons.check),
      "Check",
    );
    const resetBtn = h("button", { class: "btn ghost", title: "Restore the starter files", onclick: () => this.reset() }, icon(icons.reset));

    const editorHost = h("div", { class: "editor-host" });
    const editorPane = h(
      "section",
      { class: "pane" },
      h("div", { class: "tabs" }, fileTabs, h("div", { class: "tools" }, this.saveState, resetBtn, runBtn, this.checkBtn)),
      editorHost,
    );

    this.termTab = h("button", { class: "tab on", onclick: () => this.showBottom("term") }, "Terminal");
    this.resultsTab = h("button", { class: "tab", onclick: () => this.showBottom("results") }, "Results", this.resultsCount);
    this.resultsBox.hidden = true;
    this.resultsBox.append(
      h("div", { class: "empty" }, h("h2", null, "No results yet"), h("p", null, l.has_tests ? "Press Check to run the hidden tests." : "This lesson has no tests: explore freely.")),
    );
    const bottomPane = h(
      "section",
      { class: "pane" },
      h("div", { class: "tabs" }, this.termTab, this.resultsTab, h("div", { class: "tools" }, h("span", { class: "lbl" }, l.run ? `run: ${l.run}` : ""))),
      this.term.el,
      this.resultsBox,
    );

    const work = h("div", { class: "work", style: `--top:${stored("split.top", 58)}%` }, editorPane, this.gutter("h"), bottomPane);
    const split = h("div", { class: "split", style: `--left:${stored("split.left", 42)}%` }, left, this.gutter("v"), work);
    root.append(head, split);

    this.editor = new CodeEditor(editorHost, {
      onChange: () => this.markDirty(),
      onSave: () => void this.flush(),
      onRun: () => this.run(),
      onCheck: () => void this.check(),
    });
    void this.loadFiles();
    void this.term.mount();
    this.pollTimer = window.setInterval(() => void this.poll(), 2500);
  }

  // ---------- files ----------

  private async loadFiles() {
    const first = this.lesson.files[0];
    await Promise.all(
      this.lesson.files.map(async (name) => {
        try {
          const f = await api.readFile(this.lesson.id, name);
          if (this.disposed) return;
          this.editor.setFile(name, f.content);
          const st = this.files.get(name)!;
          st.mtime = f.mtime;
        } catch (e) {
          toast(`Could not open ${name}: ${e instanceof Error ? e.message : e}`, true);
        }
      }),
    );
    if (first && !this.disposed) {
      this.showFile(first);
      this.editor.focus();
    }
  }

  private showFile(name: string) {
    this.active = name;
    this.editor.show(name);
    for (const [n, st] of this.files) st.tab.classList.toggle("on", n === name);
  }

  private markDirty() {
    const st = this.files.get(this.active);
    if (!st) return;
    st.dirty = true;
    st.dot.hidden = false;
    this.paintSave();
    clearTimeout(this.saveTimer);
    this.saveTimer = window.setTimeout(() => void this.flush(), 700);
  }

  private paintSave() {
    const dirty = [...this.files.values()].some((f) => f.dirty);
    this.saveState.textContent = dirty ? "edited" : "saved";
    this.saveState.classList.toggle("dirty", dirty);
  }

  /** Save every edited file now. */
  private async flush() {
    clearTimeout(this.saveTimer);
    await Promise.all(
      [...this.files.entries()].map(async ([name, st]) => {
        if (st.saving) await st.saving;
        if (!st.dirty) return;
        st.dirty = false;
        const text = this.editor.text(name);
        st.saving = api
          .writeFile(this.lesson.id, name, text)
          .then((r) => {
            st.mtime = r.mtime;
            if (!st.dirty) st.dot.hidden = true;
          })
          .catch((e) => {
            st.dirty = true;
            toast(`Save failed for ${name}: ${e instanceof Error ? e.message : e}`, true);
          })
          .finally(() => {
            st.saving = null;
            this.paintSave();
          });
        await st.saving;
      }),
    );
    this.paintSave();
  }

  /** Pick up edits made from the terminal (vim, nano, a script) unless the editor has unsaved changes. */
  private async poll() {
    if (document.hidden || this.disposed) return;
    let mt: Record<string, number>;
    try {
      mt = await api.mtimes(this.lesson.id);
    } catch {
      return;
    }
    for (const [name, st] of this.files) {
      if (st.dirty || st.saving || !mt[name] || mt[name] <= st.mtime) continue;
      try {
        const f = await api.readFile(this.lesson.id, name);
        if (st.dirty || st.saving || this.disposed) continue;
        this.editor.setFile(name, f.content, { replace: true });
        st.mtime = f.mtime;
      } catch {
        /* next poll */
      }
    }
  }

  // ---------- actions ----------

  private async run() {
    if (!this.lesson.run) return;
    await this.flush();
    this.showBottom("term");
    this.term.send(this.lesson.run + "\r");
  }

  private async check() {
    if (!this.lesson.has_tests || this.checkBtn.disabled) return;
    await this.flush();
    this.checkBtn.disabled = true;
    const label = this.checkBtn.lastChild as Text;
    label.textContent = "Checking";
    this.showBottom("results");
    clear(this.resultsBox);
    this.resultsBox.append(
      h(
        "div",
        { class: "empty" },
        h("h2", null, "Running tests"),
        h("p", null, this.lesson.lang === "rust" ? "Compiling first. The first build of a crate takes longest." : "One moment."),
      ),
    );
    try {
      const r = await api.check(this.lesson.id);
      if (this.disposed) return;
      const wasPassed = this.lesson.status === "passed";
      this.lesson.status = r.status;
      this.lesson.attempts = r.attempts;
      this.paintStatus();
      this.paintResults(r);
      if (r.result.passed && !wasPassed) this.shell.invalidateTracks();
    } catch (e) {
      clear(this.resultsBox);
      this.resultsBox.append(h("div", { class: "empty" }, h("h2", null, "Check failed to run"), h("p", null, e instanceof Error ? e.message : String(e))));
    } finally {
      this.checkBtn.disabled = false;
      label.textContent = "Check";
    }
  }

  private async hint() {
    try {
      const r = await api.hint(this.lesson.id);
      this.lesson.hints = r.hints;
      this.paintHints(r.hints);
      this.hintsBox.lastElementChild?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (e) {
      toast(`Hint failed: ${e instanceof Error ? e.message : e}`, true);
    }
  }

  private async reset() {
    if (!confirm(`Reset ${this.lesson.title} to the starter files?\n\nYour current files are moved to ~/learn/.reset-backups, not deleted.`)) return;
    clearTimeout(this.saveTimer);
    for (const st of this.files.values()) st.dirty = false;
    try {
      const r = await api.reset(this.lesson.id);
      for (const name of this.lesson.files) {
        const f = await api.readFile(this.lesson.id, name);
        this.editor.setFile(name, f.content, { replace: true });
        const st = this.files.get(name)!;
        st.mtime = f.mtime;
        st.dot.hidden = true;
      }
      this.paintSave();
      this.term.restart(); // the server ended the shell that sat in the old directory
      toast(r.backup ? `Reset. Previous files saved to ${r.backup}` : "Reset to starter files");
    } catch (e) {
      toast(`Reset failed: ${e instanceof Error ? e.message : e}`, true);
    }
  }

  // ---------- painting ----------

  private paintStatus() {
    const s = this.lesson.status;
    this.statusBadge.className = `badge ${s === "passed" ? "passed" : s === "started" ? "started" : ""}`;
    this.statusBadge.textContent = s === "passed" ? "passed" : this.lesson.attempts ? `${this.lesson.attempts} attempt${this.lesson.attempts === 1 ? "" : "s"}` : "in progress";
  }

  private paintHints(hints: string[]) {
    const total = this.lesson.hints_total;
    clear(this.hintsBox);
    this.hintsBox.append(
      h(
        "div",
        { class: "phead" },
        h("h2", null, "Hints"),
        h("span", { class: "lbl" }, `${hints.length} / ${total}`),
        hints.length < total
          ? h("button", { class: "btn am", onclick: () => void this.hint() }, icon(icons.bulb), hints.length ? "Another hint" : "Show a hint")
          : null,
      ),
      ...hints.map((hint) => html("div", "hint", hint)),
    );
  }

  private paintResults(r: CheckResponse) {
    const res = r.result;
    const tests = res.tests ?? [];
    const failed = tests.filter((t) => !t.passed).length;
    const secs = (res.duration_ms / 1000).toFixed(1);

    let headline: string;
    let cls: string;
    switch (res.status) {
      case "passed":
        headline = `All ${tests.length} tests passed`;
        cls = "passed";
        break;
      case "failed":
        headline = `${failed} of ${tests.length} tests failing`;
        cls = "failed";
        break;
      case "timeout":
        headline = "Timed out";
        cls = "failed";
        break;
      default:
        headline = this.lesson.lang === "rust" ? "Did not compile" : "Tests could not run";
        cls = "failed";
    }

    this.resultsCount.hidden = false;
    this.resultsCount.className = `count ${res.passed ? "passed" : "failed"}`;
    this.resultsCount.textContent = tests.length ? `${tests.length - failed}/${tests.length}` : "!";

    const next = this.lesson.next;
    clear(this.resultsBox);
    this.resultsBox.append(
      h(
        "div",
        { class: "res-summary" },
        h("span", { class: `big ${cls}` }, headline),
        h("span", { class: "lbl" }, `${secs}s · attempt ${r.attempts}`),
        res.passed && next
          ? h("button", { class: "btn primary", style: "margin-left:auto", onclick: () => navigate(`/learn/${next.id}`) }, "Next lesson", icon(icons.right))
          : null,
      ),
      ...tests.map((t) =>
        h(
          "div",
          { class: t.passed ? "test ok" : "test bad" },
          h("span", { class: "mk" }, t.passed ? "✓" : "✗"),
          h("div", { style: "min-width:0" }, t.name, !t.passed && t.message ? h("pre", null, t.message) : null),
        ),
      ),
    );
    const raw = h("details", { class: "raw", open: !tests.length || res.status === "timeout" }, h("summary", { class: "lbl" }, "Raw output"), h("pre", { class: "raw-out" }, res.output || "(no output)"));
    this.resultsBox.append(raw);
    if (res.status === "timeout") {
      this.resultsBox.prepend(h("div", { class: "banner", style: "margin:12px 16px 0" }, "The tests did not finish in time. Look for an infinite loop, or a program waiting for input()."));
    }
  }

  private showBottom(which: "term" | "results") {
    const t = which === "term";
    this.termTab.classList.toggle("on", t);
    this.resultsTab.classList.toggle("on", !t);
    this.term.el.hidden = !t;
    this.resultsBox.hidden = t;
    if (t) requestAnimationFrame(() => this.term.resize());
  }

  /** Drag handle between panes; sizes are remembered as percentages. */
  private gutter(dir: "v" | "h"): HTMLElement {
    const g = h("div", { class: dir === "v" ? "gutter" : "gutter h", role: "separator" });
    g.addEventListener("pointerdown", (e) => {
      const container = g.parentElement!;
      const rect = container.getBoundingClientRect();
      g.setPointerCapture(e.pointerId);
      g.classList.add("drag");
      const move = (ev: PointerEvent) => {
        const p =
          dir === "v"
            ? ((ev.clientX - rect.left) / rect.width) * 100
            : ((ev.clientY - rect.top) / rect.height) * 100;
        const clamped = Math.max(18, Math.min(82, p));
        container.style.setProperty(dir === "v" ? "--left" : "--top", `${clamped}%`);
        store(dir === "v" ? "split.left" : "split.top", Math.round(clamped));
        this.term.resize();
      };
      const up = () => {
        g.classList.remove("drag");
        g.removeEventListener("pointermove", move);
        g.removeEventListener("pointerup", up);
      };
      g.addEventListener("pointermove", move);
      g.addEventListener("pointerup", up);
    });
    return g;
  }

  private dispose() {
    this.disposed = true;
    clearInterval(this.pollTimer);
    void this.flush();
    this.term.dispose();
    this.editor?.destroy();
  }
}
