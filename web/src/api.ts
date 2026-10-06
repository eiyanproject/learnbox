export type Status = "" | "started" | "passed";

export interface LessonSummary {
  id: string;
  slug: string;
  title: string;
  summary: string;
  difficulty?: number;
  has_tests: boolean;
  status: Status;
  kind?: string;
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
  /** "misc" for tracks shown apart from the programming ones. */
  group?: string;
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
  kind?: string;
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
  /** What passing pays with no hints, and what it pays (or paid) this learner. */
  xp_full: number;
  xp: number;
  /** XP the next hint would take off; 0 once passed or out of hints. */
  hint_cost: number;
  /** Set for an arena challenge: how it stands, and the server's time. */
  arena: { now: string; challenge: ChallengeView } | null;
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
  /** Null when an arena check arrives after the clock ran out. */
  result: CheckResult | null;
  status: Status;
  attempts: number;
  reward: Reward;
  // The rest is only there for an arena challenge.
  now?: string;
  challenge?: ChallengeView;
  outcome?: "" | "won" | "lost";
  challenge_xp?: number;
}

export type ChallengeState = "locked" | "ready" | "active" | "cooldown" | "won";

export interface ChallengeView {
  id: string;
  title: string;
  summary: string;
  boss: boolean;
  minutes: number;
  cooldown_minutes: number;
  xp: number;
  max_xp: number;
  state: ChallengeState;
  locks: string[];
  deadline?: string;
  cooldown_until?: string;
  wins: number;
  losses: number;
  best_seconds?: number;
  best_xp?: number;
}

export interface Ladder {
  lang: string;
  title: string;
  track_xp: number;
  challenges: ChallengeView[];
}

export interface ArenaResponse {
  now: string;
  ladders: Ladder[];
}

export interface ChallengeResponse {
  now: string;
  challenge: ChallengeView;
}

export interface Standing {
  xp: number;
  level: number;
  title: string;
  /** XP totals at which this level and the next one start. */
  level_floor: number;
  next_level: number;
}

export type BadgeFamily = "milestone" | "completion" | "style" | "calendar" | "arena" | "secret";

export interface Badge {
  id: string;
  name: string;
  description: string;
  family: BadgeFamily;
  earned: boolean;
  earned_at?: string;
  have: number;
  want: number;
}

export interface TrackXP {
  lang: string;
  title: string;
  xp: number;
  possible: number;
}

export interface Summary extends Standing {
  passed: number;
  tracks: TrackXP[];
  badges: Badge[];
}

/** What one check earned. */
export interface Reward {
  xp: number;
  level_up: boolean;
  badges: Badge[];
  standing: Standing;
}

export interface ServerStatus {
  version: string;
  tools: { python: string; rust: string };
  limits_active: boolean;
  sessions: number;
  lessons: number;
}

export interface Profile {
  id: string;
  name: string;
  created_at: string;
}

export interface ProfilesResponse {
  profiles: Profile[];
  /** Empty when several profiles exist and this browser has not picked one. */
  current: string;
}

// ---------- quiz ----------

export interface QuizStatement {
  en: string;
  ja: string;
}

export interface QuizQuestion {
  id: string;
  kind?: "scenario";
  en: string;
  ja: string;
  topic: string;
  /** A picture that goes with the question, fetched from where it is hosted. */
  image?: string;
  statements?: QuizStatement[];
}

export interface QuizGiven {
  answer?: boolean;
  answers?: boolean[];
}

export interface QuizExplanation {
  id: string;
  correct: boolean;
  answer?: boolean;
  why?: string;
  ref: string;
  statements?: (QuizStatement & { answer: boolean; why: string })[];
  given?: QuizGiven;
  question?: QuizQuestion;
}

export interface ExamSpec {
  id: string;
  title: string;
  tf: number;
  scenarios: number;
  minutes: number;
  tf_points: number;
  scenario_points: number;
  pass: number;
  max: number;
}

export interface ExamResult {
  exam: string;
  at: string;
  score: number;
  max: number;
  passed: boolean;
  seconds: number;
  overtime?: boolean;
  wrong?: string[];
}

export interface QuizOverview {
  track: string;
  title: string;
  description: string;
  total: number;
  mistakes: number;
  clear_after: number;
  sections: {
    id: string;
    title: string;
    topics: { id: string; title: string; summary: string; total: number; mastered: number; mistakes: number }[];
  }[];
  exams: (ExamSpec & {
    pool: number;
    scenario_pool: number;
    ready: boolean;
    deadline?: string;
    best?: ExamResult;
    recent: ExamResult[];
    attempts: number;
    pass_streak: number;
  })[];
}

export interface QuizTopic {
  id: string;
  title: string;
  summary: string;
  notes_html: string;
  track: string;
  track_title: string;
  questions: (QuizQuestion & { mistake: boolean; right_before: boolean })[];
  prev: LessonLink | null;
  next: LessonLink | null;
}

export interface ExamStart {
  spec: ExamSpec;
  started: string;
  deadline: string;
  now: string;
  questions: QuizQuestion[];
}

/** Where a quiz lesson (lang/section/slug) is studied. */
export function quizHref(lessonID: string) {
  const [track, section, slug] = lessonID.split("/");
  return `/quiz/${track}/topic/${section}/${slug}`;
}

/** Fired when the server needs a profile picked before it can answer. */
export const CHOOSE_PROFILE = "learnbox:choose-profile";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    /** The server's machine-readable reason, when it gave one. */
    public code = "",
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
    if (res.status === 409 && (data as { code?: string } | null)?.code === "choose_profile") {
      window.dispatchEvent(new CustomEvent(CHOOSE_PROFILE));
    }
    const msg = (data as { error?: string } | null)?.error ?? `${res.status} ${res.statusText}`;
    throw new ApiError(res.status, msg, (data as { code?: string } | null)?.code ?? "");
  }
  return data as T;
}

const L = (id: string) => `/api/lessons/${id}`;
const F = (id: string, name: string) => `${L(id)}/files/${name.split("/").map(encodeURIComponent).join("/")}`;

export const api = {
  status: () => call<ServerStatus>("GET", "/api/status"),
  tracks: () => call<TracksResponse>("GET", "/api/tracks"),
  summary: () => call<Summary>("GET", "/api/summary"),
  arena: () => call<ArenaResponse>("GET", "/api/arena"),
  startChallenge: (id: string) => call<ChallengeResponse>("POST", `${L(id)}/challenge/start`),
  forfeitChallenge: (id: string) => call<ChallengeResponse>("POST", `${L(id)}/challenge/forfeit`),
  lesson: (id: string) => call<Lesson>("GET", L(id)),
  readFile: (id: string, name: string) => call<FileBody>("GET", F(id, name)),
  writeFile: (id: string, name: string, content: string) => call<{ mtime: number }>("PUT", F(id, name), { content }),
  mtimes: (id: string) => call<Record<string, number>>("GET", `${L(id)}/mtimes`),
  check: (id: string) => call<CheckResponse>("POST", `${L(id)}/check`),
  hint: (id: string) => call<{ hints: string[]; hints_total: number; xp: number; hint_cost: number }>("POST", `${L(id)}/hint`),
  reset: (id: string) => call<{ status: string; backup?: string }>("POST", `${L(id)}/reset`),
  quiz: (track: string) => call<QuizOverview>("GET", `/api/quiz/${track}`),
  quizTopic: (track: string, section: string, slug: string) => call<QuizTopic>("GET", `/api/quiz/${track}/topic/${section}/${slug}`),
  quizAnswer: (track: string, id: string, given: QuizGiven) =>
    call<{ result: QuizExplanation; topic_mastered: boolean }>("POST", `/api/quiz/${track}/answer`, { id, ...given }),
  quizMistakes: (track: string) => call<{ questions: QuizQuestion[]; clear_after: number }>("GET", `/api/quiz/${track}/mistakes`),
  examStart: (track: string, exam: string) => call<ExamStart>("POST", `/api/quiz/${track}/exam/${exam}`),
  examSubmit: (track: string, exam: string, answers: Record<string, QuizGiven>) =>
    call<{ result: ExamResult; review: QuizExplanation[] }>("POST", `/api/quiz/${track}/exam/${exam}/submit`, { answers }),
  examAbandon: (track: string, exam: string) => call<{ status: string }>("DELETE", `/api/quiz/${track}/exam/${exam}`),
  profiles: () => call<ProfilesResponse>("GET", "/api/profiles"),
  createProfile: (name: string) => call<Profile>("POST", "/api/profiles", { name }),
  selectProfile: (id: string) => call<Profile>("POST", `/api/profiles/${encodeURIComponent(id)}/select`),
  renameProfile: (id: string, name: string) => call<Profile>("POST", `/api/profiles/${encodeURIComponent(id)}/rename`, { name }),
  deleteProfile: (id: string) => call<{ status: string; files: string }>("DELETE", `/api/profiles/${encodeURIComponent(id)}`),
};
