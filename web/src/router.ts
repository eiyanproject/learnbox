export interface Page {
  /** Called before navigating away. Return false to cancel (unsaved work). */
  beforeLeave?: () => boolean;
  dispose?: () => void;
}

type Handler = (params: Record<string, string>) => Page | Promise<Page>;

const routes: { re: RegExp; keys: string[]; handler: Handler }[] = [];
let current: Page | null = null;
let seq = 0;

export function route(pattern: string, handler: Handler) {
  const keys: string[] = [];
  const re = new RegExp(
    "^" +
      pattern.replace(/:(\w+)/g, (_, k) => {
        keys.push(k);
        return "([^/]+)";
      }) +
      "/?$",
  );
  routes.push({ re, keys, handler });
}

export function navigate(path: string, { replace = false } = {}) {
  if (path === location.pathname) return;
  if (current?.beforeLeave && !current.beforeLeave()) return;
  if (replace) history.replaceState(null, "", path);
  else history.pushState(null, "", path);
  void render();
}

export async function render() {
  const my = ++seq;
  const path = location.pathname;
  for (const r of routes) {
    const m = path.match(r.re);
    if (!m) continue;
    const params: Record<string, string> = {};
    r.keys.forEach((k, i) => (params[k] = decodeURIComponent(m[i + 1])));
    current?.dispose?.();
    current = null;
    const page = await r.handler(params);
    if (my !== seq) {
      page.dispose?.(); // a newer navigation won the race
      return;
    }
    current = page;
    return;
  }
  history.replaceState(null, "", "/");
  void render();
}

export function start() {
  window.addEventListener("popstate", () => void render());
  window.addEventListener("beforeunload", (e) => {
    if (current?.beforeLeave && !current.beforeLeave()) e.preventDefault();
  });
  void render();
}
