# learnbox

Private single-user learning platform: Go service (`cmd/learnbox`, `internal/`),
Vite + TypeScript frontend (`web/`), lessons in `content/`. README.md explains
the architecture, safety model and deploy scripts.

- Linux only. The service runs as root and starts everything learner-facing
  through `internal/sandbox` (uid drop + cgroup). Never `exec.Command` a learner
  tool directly: resolve it with `Sandbox.LookPath` and start it with `Spawn`.
- File access under the learner's home goes through `internal/workspace`
  (`os.Root`). Do not add `os.*` calls on learner-owned paths.
- Lesson Markdown is rendered with raw HTML disabled; keep it that way.
- After changing lessons, run `learnbox verify <prefix>` in the CT: every
  `solution/` must pass its tests.
- Deploy scripts follow the homelab convention: host scripts print a plan until
  `--yes`; `install.sh` is idempotent and re-run by `update.sh`.

## Observability

Every HTTP service in this repo exposes:
  - GET /healthz  - liveness, no dependency checks, unauthenticated
  - GET /readyz   - 200 only when dependencies are reachable
  - GET /metrics  - Prometheus text format via prometheus/client_golang

Metrics: <svc>_build_info, <svc>_requests_total{route,method,status},
<svc>_request_duration_seconds{route}, <svc>_errors_total{kind}.
Label with route templates, never with IDs or full paths.

Logs: single-line JSON to stdout with keys ts, level, msg, svc. Never log files.

Register new services in the monitoring repo's targets/services.json.
