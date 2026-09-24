import { keyBar } from "../components/keybar";
import { TermView } from "../components/terminal";
import { clear, h } from "../dom";
import type { Page } from "../router";
import type { Shell } from "../shell";

export function terminalPage(shell: Shell): Page {
  shell.setActive("terminal");
  shell.setFill(true);
  const root = shell.content;
  clear(root);

  const term = new TermView("scratch");
  root.append(
    h(
      "div",
      { class: "lesson-head" },
      h(
        "div",
        { class: "crumbs" },
        h("span", { class: "lbl" }, "Free terminal · ~ · python, cargo, git"),
        h("h1", null, "Scratch shell"),
      ),
    ),
    h("div", { class: "pane term-page" }, term.el, keyBar(term)),
  );
  void term.mount().then(() => term.focus());
  return { dispose: () => term.dispose() };
}
