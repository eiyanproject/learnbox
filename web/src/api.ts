export type Status = "" | "started" | "passed";

export interface LessonSummary {
  id: string;
  slug: string;
  title: string;
  summary: string;
  difficulty?: number;
  has_tests: boolean;
  status: Status;
}

export interface Section {
  id: string;
  title: string;
  description: string;
  lessons: LessonSummary[];
  passed: number;
}

export interface Track {
  lang: string;
  title: string;
  description: string;
  sections: Section[];
  total: number;
  passed: number;
}

export interface TracksResponse {
  tracks: Track[];
  last_lesson?: { id: string; title: string };
}

export interface LessonLink {
  id: string;
  title: string;
}

export interface Lesson {
  id: string;
  lang: string;
  section: string;
  slug: string;
  title: string;
  summary: string;
  html: string;
  source_html: string;
  track_title: string;
  section_title: string;
  files: string[];
  run: string;
  has_tests: boolean;
  hints_total: number;
  hints: string[];
  status: Status;
  attempts: number;
  workspace: string;
  prev: LessonLink | null;
  next: LessonLink | null;
}

export interface FileBody {
  name: string;
  content: string;
  mtime: number;
  missing?: boolean;
}

export interface TestResult {
  name: string;
  passed: boolean;
  message?: string;
}

export interface CheckResult {
  status: "passed" | "failed" | "error" | "timeout";
  passed: boolean;
  tests: TestResult[] | null;
  output: string;
  duration_ms: number;
}

export interface CheckResponse {
  result: CheckResult;
  status: Status;
  attempts: number;
}

export interface ServerStatus {
  version: string;
  tools: { python: string; rust: string };
  limits_active: boolean;
  sessions: number;
  lessons: number;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function call<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = {};
  if (method !== "GET") headers["X-Learnbox"] = "1"; // required for any change, see httpapi CSRF guard
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const res = await fetch(path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await res.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    /* non-JSON error page */
  }
  if (!res.ok) {
    const msg = (data as { error?: string } | null)?.error ?? `${res.status} ${res.statusText}`;
    throw new ApiError(res.status, msg);
  }
  return data as T;
}

const L = (id: string) => `/api/lessons/${id}`;
const F = (id: string, name: string) => `${L(id)}/files/${name.split("/").map(encodeURIComponent).join("/")}`;

export const api = {
  status: () => call<ServerStatus>("GET", "/api/status"),
  tracks: () => call<TracksResponse>("GET", "/api/tracks"),
  lesson: (id: string) => call<Lesson>("GET", L(id)),
  readFile: (id: string, name: string) => call<FileBody>("GET", F(id, name)),
  writeFile: (id: string, name: string, content: string) => call<{ mtime: number }>("PUT", F(id, name), { content }),
  mtimes: (id: string) => call<Record<string, number>>("GET", `${L(id)}/mtimes`),
  check: (id: string) => call<CheckResponse>("POST", `${L(id)}/check`),
  hint: (id: string) => call<{ hints: string[]; hints_total: number }>("POST", `${L(id)}/hint`),
  reset: (id: string) => call<{ status: string; backup?: string }>("POST", `${L(id)}/reset`),
};
