import { basicSetup } from "codemirror";
import { EditorView, keymap } from "@codemirror/view";
import { EditorState, Compartment, type Extension } from "@codemirror/state";
import { indentWithTab } from "@codemirror/commands";
import { HighlightStyle, syntaxHighlighting, indentUnit } from "@codemirror/language";
import { tags as t } from "@lezer/highlight";
import { python } from "@codemirror/lang-python";
import { rust } from "@codemirror/lang-rust";

// Colours are CSS variables, so the dark/light switch needs no reconfigure.
const chrome = EditorView.theme({
  "&": {
    height: "100%",
    backgroundColor: "var(--surf)",
    color: "var(--fg)",
    fontSize: "13.5px",
  },
  ".cm-scroller": {
    fontFamily: '"IBM Plex Mono", ui-monospace, monospace',
    lineHeight: "1.6",
  },
  ".cm-content": { caretColor: "var(--cy)", padding: "10px 0" },
  ".cm-cursor, .cm-dropCursor": { borderLeftColor: "var(--cy)", borderLeftWidth: "2px" },
  "&.cm-focused": { outline: "none" },
  "&.cm-focused > .cm-scroller > .cm-selectionLayer .cm-selectionBackground, .cm-selectionBackground, ::selection": {
    backgroundColor: "var(--sel)",
  },
  ".cm-gutters": {
    backgroundColor: "var(--surf)",
    color: "var(--dim)",
    border: "none",
    borderRight: "1px solid var(--line)",
  },
  ".cm-activeLineGutter": { backgroundColor: "var(--surf2)", color: "var(--cy)" },
  ".cm-activeLine": { backgroundColor: "color-mix(in srgb, var(--surf2) 70%, transparent)" },
  ".cm-matchingBracket, &.cm-focused .cm-matchingBracket": {
    backgroundColor: "var(--cyw)",
    outline: "1px solid var(--cyl)",
  },
  ".cm-searchMatch": { backgroundColor: "var(--amw)", outline: "1px solid var(--aml)" },
  ".cm-panels": { backgroundColor: "var(--surf2)", color: "var(--fg)", borderTop: "1px solid var(--line)" },
  ".cm-tooltip": { backgroundColor: "var(--surf2)", border: "1px solid var(--line)" },
  ".cm-tooltip-autocomplete ul li[aria-selected]": { backgroundColor: "var(--cyw)", color: "var(--cy)" },
  ".cm-foldPlaceholder": { backgroundColor: "var(--surf2)", border: "1px solid var(--line)", color: "var(--mut)" },
});

const highlight = HighlightStyle.define([
  { tag: [t.keyword, t.controlKeyword, t.moduleKeyword, t.operatorKeyword, t.self], color: "var(--syn-kw)" },
  { tag: [t.string, t.special(t.string), t.character], color: "var(--syn-str)" },
  { tag: [t.number, t.bool, t.null, t.atom], color: "var(--syn-num)" },
  { tag: [t.function(t.variableName), t.function(t.propertyName), t.macroName], color: "var(--syn-fn)" },
  { tag: [t.typeName, t.className, t.namespace, t.definition(t.typeName)], color: "var(--syn-type)" },
  { tag: [t.comment, t.lineComment, t.blockComment, t.docComment], color: "var(--syn-com)", fontStyle: "italic" },
  { tag: [t.operator, t.punctuation, t.bracket, t.derefOperator], color: "var(--syn-op)" },
  { tag: [t.variableName, t.propertyName], color: "var(--syn-var)" },
  { tag: [t.attributeName, t.meta, t.special(t.variableName)], color: "var(--am)" },
  { tag: t.invalid, color: "var(--am)", textDecoration: "underline wavy" },
]);

function languageFor(name: string): Extension {
  if (name.endsWith(".py")) return python();
  if (name.endsWith(".rs")) return rust();
  return [];
}

export interface EditorHooks {
  onChange: () => void;
  onSave: () => void;
  onRun: () => void;
  onCheck: () => void;
}

/** One CodeMirror view; files are swapped in as separate EditorStates so each keeps its own undo history. */
export class CodeEditor {
  readonly view: EditorView;
  private states = new Map<string, EditorState>();
  private current = "";
  private lang = new Compartment();
  private silent = false; // programmatic reloads are not edits

  constructor(parent: HTMLElement, private hooks: EditorHooks) {
    this.view = new EditorView({ parent, state: this.makeState("", "") });
  }

  private makeState(name: string, doc: string): EditorState {
    const hooks = this.hooks;
    return EditorState.create({
      doc,
      extensions: [
        basicSetup,
        keymap.of([
          indentWithTab,
          { key: "Mod-s", preventDefault: true, run: () => (hooks.onSave(), true) },
          { key: "Mod-Enter", preventDefault: true, run: () => (hooks.onRun(), true) },
          { key: "Mod-Shift-Enter", preventDefault: true, run: () => (hooks.onCheck(), true) },
        ]),
        indentUnit.of("    "),
        EditorState.tabSize.of(4),
        chrome,
        syntaxHighlighting(highlight),
        this.lang.of(languageFor(name)),
        EditorView.updateListener.of((u) => {
          if (u.docChanged && !this.silent) hooks.onChange();
        }),
      ],
    });
  }

  /** Load or replace a file's text. Keeps undo history unless the file is new. */
  setFile(name: string, text: string, { replace = false } = {}) {
    const existing = this.states.get(name);
    if (existing && !replace) return;
    if (existing && replace) {
      if (name === this.current) {
        const sel = this.view.state.selection.main.head;
        this.silent = true;
        try {
          this.view.dispatch({
            changes: { from: 0, to: this.view.state.doc.length, insert: text },
            selection: { anchor: Math.min(sel, text.length) },
          });
        } finally {
          this.silent = false;
        }
        return;
      }
      const tr = existing.update({ changes: { from: 0, to: existing.doc.length, insert: text } });
      this.states.set(name, tr.state);
      return;
    }
    this.states.set(name, this.makeState(name, text));
  }

  show(name: string) {
    if (this.current) this.states.set(this.current, this.view.state);
    const st = this.states.get(name);
    if (!st) return;
    this.current = name;
    this.view.setState(st);
  }

  text(name: string): string {
    if (name === this.current) return this.view.state.doc.toString();
    return this.states.get(name)?.doc.toString() ?? "";
  }

  focus() {
    this.view.focus();
  }

  destroy() {
    this.view.destroy();
  }
}
