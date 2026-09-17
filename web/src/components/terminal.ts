import { Terminal, type ITheme } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebLinksAddon } from "@xterm/addon-web-links";
import "@xterm/xterm/css/xterm.css";

import { h } from "../dom";
import { cssVar, onTheme } from "../theme";

function xtermTheme(): ITheme {
  const dark = document.documentElement.dataset.theme !== "light";
  const v = cssVar;
  return {
    background: v("--surf"),
    foreground: v("--fg"),
    cursor: v("--cy"),
    cursorAccent: v("--surf"),
    selectionBackground: dark ? "rgba(53,224,208,0.28)" : "rgba(0,128,122,0.22)",
    black: dark ? "#1f2b3a" : "#0c141e",
    brightBlack: dark ? "#48586b" : "#57677a",
    red: dark ? "#ff6b7a" : "#b3263e",
    brightRed: dark ? "#ff8c98" : "#cf3450",
    green: dark ? "#6ee7a8" : "#1d7a4a",
    brightGreen: dark ? "#95f0c1" : "#239058",
    yellow: v("--am"),
    brightYellow: dark ? "#ffc97d" : "#b87a0a",
    blue: dark ? "#6aa8ff" : "#1f5fbf",
    brightBlue: dark ? "#93c0ff" : "#2d72d6",
    magenta: v("--mg"),
    brightMagenta: dark ? "#ff8cc0" : "#d63d85",
    cyan: v("--cy"),
    brightCyan: dark ? "#7af0e5" : "#0a9a92",
    white: dark ? "#dce6f0" : "#d3dbe3",
    brightWhite: dark ? "#ffffff" : "#f2f5f8",
  };
}

type State = "connecting" | "live" | "exited" | "offline";

/**
 * An xterm.js view bound to a server-side shell session. The session lives on
 * the server; this component can be destroyed and recreated freely and will
 * reattach with the recent scrollback.
 */
export class TermView {
  readonly el: HTMLElement;
  private term: Terminal;
  private fit = new FitAddon();
  private ws: WebSocket | null = null;
  private state: State = "connecting";
  private retry = 0;
  private retryTimer = 0;
  private disposed = false;
  private enc = new TextEncoder();
  private note: HTMLElement;
  private ro: ResizeObserver;
  private offTheme: () => void;

  constructor(private session: string) {
    this.note = h("span", { class: "badge term-note", hidden: true });
    const host = h("div", { class: "term-host" }, this.note);
    this.el = host;

    this.term = new Terminal({
      fontFamily: '"IBM Plex Mono", ui-monospace, monospace',
      fontSize: 13,
      lineHeight: 1.2,
      cursorBlink: true,
      scrollback: 5000,
      allowProposedApi: false,
      theme: xtermTheme(),
    });
    this.term.loadAddon(this.fit);
    this.term.loadAddon(new WebLinksAddon());

    this.term.onData((d) => {
      if (this.state === "exited") {
        if (d === "\r") this.connect();
        return;
      }
      this.sendBytes(this.enc.encode(d));
    });
    this.term.onBinary((d) => {
      const bytes = new Uint8Array(d.length);
      for (let i = 0; i < d.length; i++) bytes[i] = d.charCodeAt(i) & 0xff;
      this.sendBytes(bytes);
    });

    this.ro = new ResizeObserver(() => this.resize());
    this.offTheme = onTheme(() => {
      this.term.options.theme = xtermTheme();
    });
  }

  /** Call once the element is in the document. */
  async mount() {
    // xterm measures the font once; measure the real one, not the fallback.
    try {
      await document.fonts.load('13px "IBM Plex Mono"');
    } catch {
      /* measure with fallback */
    }
    if (this.disposed) return;
    this.term.open(this.el);
    this.ro.observe(this.el);
    this.resize();
    this.connect();
  }

  focus() {
    this.term.focus();
  }

  /** Type text into the shell as if the learner had. */
  send(text: string) {
    if (this.state !== "live") {
      this.connect();
      setTimeout(() => this.send(text), 400);
      return;
    }
    this.sendBytes(this.enc.encode(text));
    this.term.focus();
  }

  /** Drop the current connection and attach again (a new shell if the old one ended). */
  restart() {
    setTimeout(() => this.connect(), 300);
  }

  resize() {
    if (!this.el.isConnected || this.el.clientWidth === 0) return;
    try {
      this.fit.fit();
    } catch {
      return;
    }
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: "resize", cols: this.term.cols, rows: this.term.rows }));
    }
  }

  dispose() {
    this.disposed = true;
    clearTimeout(this.retryTimer);
    this.ro.disconnect();
    this.offTheme();
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.close();
    }
    this.term.dispose();
  }

  private sendBytes(b: Uint8Array<ArrayBuffer>) {
    if (this.ws?.readyState === WebSocket.OPEN) this.ws.send(b);
  }

  private setState(s: State, note = "") {
    this.state = s;
    this.note.hidden = s === "live";
    this.note.textContent = note;
  }

  private connect() {
    if (this.disposed) return;
    clearTimeout(this.retryTimer);
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.close();
    }
    this.setState("connecting", "connecting");
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/api/term?session=${encodeURIComponent(this.session)}`);
    ws.binaryType = "arraybuffer";
    this.ws = ws;

    ws.onopen = () => {
      this.retry = 0;
      // The server replays recent output on attach; start from a clean screen
      // so a reconnect does not duplicate it.
      this.term.reset();
      this.setState("live");
      this.resize();
    };
    ws.onmessage = (ev) => {
      if (typeof ev.data === "string") {
        try {
          const msg = JSON.parse(ev.data) as { type: string; code?: number };
          if (msg.type === "exit") {
            this.setState("exited", `exited ${msg.code ?? 0}`);
            this.term.write(`\r\n\x1b[2m[shell exited with code ${msg.code ?? 0}; press Enter for a new one]\x1b[0m\r\n`);
          }
        } catch {
          /* ignore */
        }
        return;
      }
      this.term.write(new Uint8Array(ev.data as ArrayBuffer));
    };
    ws.onclose = (ev) => {
      if (this.disposed || this.state === "exited") return;
      if (ev.code === 1008) {
        // Taken over by another tab: do not fight over the session.
        this.setState("offline", "open in another tab");
        this.term.write("\r\n\x1b[2m[this terminal was opened in another tab; press Enter to take it back]\x1b[0m\r\n");
        this.state = "exited";
        return;
      }
      this.setState("offline", "reconnecting");
      const delay = Math.min(8000, 400 * 2 ** this.retry++);
      this.retryTimer = window.setTimeout(() => this.connect(), delay);
    };
  }
}
