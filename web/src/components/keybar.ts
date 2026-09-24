import { h } from "../dom";
import type { TermView } from "./terminal";

/**
 * A row of keys a phone keyboard does not have.
 *
 * Esc, Tab, Ctrl-C and the arrows are not optional extras in a terminal: no
 * history, no completion, and no way to stop a runaway command without them.
 * Software keyboards on both iOS and Android omit all four.
 *
 * There is no sticky Ctrl. Letters arrive from the system keyboard, which the
 * page cannot intercept reliably, so the combinations that matter are offered
 * whole instead of as a modifier the next key has to pair with.
 */
const KEYS: Array<[label: string, send: string, title: string]> = [
  ["esc", "\x1b", "Escape"],
  ["tab", "\t", "Tab - completion"],
  ["^C", "\x03", "Ctrl-C - interrupt"],
  ["^D", "\x04", "Ctrl-D - end of input"],
  ["^Z", "\x1a", "Ctrl-Z - suspend"],
  ["^L", "\x0c", "Ctrl-L - clear"],
  ["↑", "\x1b[A", "Previous command"],
  ["↓", "\x1b[B", "Next command"],
  ["←", "\x1b[D", "Left"],
  ["→", "\x1b[C", "Right"],
  ["|", "|", "Pipe"],
  ["~", "~", "Home directory"],
  ["/", "/", "Slash"],
  ["-", "-", "Dash"],
];

export function keyBar(term: TermView): HTMLElement {
  const bar = h("div", { class: "keybar", role: "toolbar", "aria-label": "Terminal keys" });
  for (const [label, seq, title] of KEYS) {
    bar.append(
      h(
        "button",
        {
          class: "keycap",
          type: "button",
          title,
          "aria-label": title,
          // pointerdown, not click: the terminal's textarea must not lose focus,
          // or the software keyboard closes on every key.
          onpointerdown: (e: Event) => {
            e.preventDefault();
            term.send(seq);
          },
        },
        label,
      ),
    );
  }
  return bar;
}
