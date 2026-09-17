export type Theme = "dark" | "light";

const KEY = "learnbox.theme";
const listeners = new Set<(t: Theme) => void>();

export function theme(): Theme {
  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

export function setTheme(t: Theme) {
  document.documentElement.dataset.theme = t;
  try {
    localStorage.setItem(KEY, t);
  } catch {
    /* storage blocked */
  }
  listeners.forEach((fn) => fn(t));
}

export function toggleTheme() {
  setTheme(theme() === "dark" ? "light" : "dark");
}

export function onTheme(fn: (t: Theme) => void): () => void {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

/** Resolved value of a CSS custom property, for libraries that need real colours. */
export function cssVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

export function stored<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(`learnbox.${key}`);
    return raw === null ? fallback : (JSON.parse(raw) as T);
  } catch {
    return fallback;
  }
}

export function store(key: string, value: unknown) {
  try {
    localStorage.setItem(`learnbox.${key}`, JSON.stringify(value));
  } catch {
    /* storage blocked */
  }
}
