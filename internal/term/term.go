// Package term keeps bash sessions alive in PTYs and streams them over
// WebSocket. A session outlives its browser tab: reopening the page
// reattaches and replays recent output, so moving between lessons does not
// throw away what was running.
//
// Wire protocol: binary frames carry raw terminal bytes in both directions.
// Text frames carry JSON control messages: {"type":"resize","cols":N,"rows":N}
// from the client, {"type":"exit","code":N} from the server.
package term

import (
	"context"
	"encoding/json"
	"errors"
	"log/slog"
	"os"
	"os/exec"
	"regexp"
	"sort"
	"sync"
	"syscall"
	"time"

	"github.com/coder/websocket"
	"github.com/creack/pty"

	"github.com/eiyanproject/learnbox/internal/sandbox"
)

const (
	replayBytes = 256 << 10
	sendQueue   = 512
)

var validID = regexp.MustCompile(`^[a-z0-9][a-z0-9/_.-]{0,120}$`)

func ValidID(id string) bool { return validID.MatchString(id) }

type Manager struct {
	sb          *sandbox.Sandbox
	log         *slog.Logger
	MaxSessions int
	IdleTimeout time.Duration // detached sessions older than this are killed

	mu       sync.Mutex
	sessions map[string]*session
}

func NewManager(sb *sandbox.Sandbox, log *slog.Logger) *Manager {
	return &Manager{sb: sb, log: log, MaxSessions: 8, IdleTimeout: 4 * time.Hour, sessions: map[string]*session{}}
}

type session struct {
	id  string
	cmd *exec.Cmd
	pty *os.File

	mu       sync.Mutex
	buf      []byte
	client   *client
	detached time.Time // zero while a client is attached
}

type client struct {
	conn *websocket.Conn
	out  chan frame
	done chan struct{}
	once sync.Once
}

type frame struct {
	typ  websocket.MessageType
	data []byte
}

func (c *client) close(code websocket.StatusCode, reason string) {
	c.once.Do(func() {
		close(c.done)
		c.conn.Close(code, reason)
	})
}

// Count returns the number of live sessions, for metrics.
func (m *Manager) Count() int {
	m.mu.Lock()
	defer m.mu.Unlock()
	return len(m.sessions)
}

// Attach connects conn to session id, starting bash in cwd if the session
// does not exist yet. It returns when the client disconnects.
func (m *Manager) Attach(ctx context.Context, id, cwd string, conn *websocket.Conn) error {
	s, err := m.getOrStart(id, cwd)
	if err != nil {
		conn.Close(websocket.StatusInternalError, "could not start shell")
		return err
	}

	c := &client{conn: conn, out: make(chan frame, sendQueue), done: make(chan struct{})}
	s.mu.Lock()
	if old := s.client; old != nil {
		old.close(websocket.StatusPolicyViolation, "opened in another tab")
	}
	// Queue the replay under the same lock pump uses to append output, so
	// nothing live can overtake it.
	if len(s.buf) > 0 {
		c.out <- frame{websocket.MessageBinary, append([]byte(nil), s.buf...)}
	}
	s.client = c
	s.detached = time.Time{}
	s.mu.Unlock()

	go c.writeLoop(ctx)

	defer func() {
		s.mu.Lock()
		if s.client == c {
			s.client = nil
			s.detached = time.Now()
		}
		s.mu.Unlock()
		c.close(websocket.StatusNormalClosure, "")
	}()

	conn.SetReadLimit(1 << 20)
	for {
		typ, data, err := conn.Read(ctx)
		if err != nil {
			return nil
		}
		switch typ {
		case websocket.MessageBinary:
			if _, err := s.pty.Write(data); err != nil {
				return nil
			}
		case websocket.MessageText:
			var msg struct {
				Type string `json:"type"`
				Cols uint16 `json:"cols"`
				Rows uint16 `json:"rows"`
			}
			if json.Unmarshal(data, &msg) == nil && msg.Type == "resize" && msg.Cols > 0 && msg.Rows > 0 {
				pty.Setsize(s.pty, &pty.Winsize{Cols: msg.Cols, Rows: msg.Rows})
			}
		}
	}
}

func (c *client) send(f frame) {
	select {
	case c.out <- f:
	case <-c.done:
	default:
		// A client that cannot keep up (a runaway print loop on a slow
		// link) is dropped rather than blocking the shell; it reconnects
		// and gets the replay buffer.
		c.close(websocket.StatusTryAgainLater, "client too slow")
	}
}

func (c *client) writeLoop(ctx context.Context) {
	for {
		select {
		case f := <-c.out:
			wctx, cancel := context.WithTimeout(ctx, 10*time.Second)
			err := c.conn.Write(wctx, f.typ, f.data)
			cancel()
			if err != nil {
				c.close(websocket.StatusGoingAway, "write failed")
				return
			}
		case <-c.done:
			return
		case <-ctx.Done():
			return
		}
	}
}

func (m *Manager) getOrStart(id, cwd string) (*session, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if s := m.sessions[id]; s != nil {
		return s, nil
	}
	m.evictLocked()

	var ptmx *os.File
	cmd, err := m.sb.Spawn(func() *exec.Cmd {
		c := exec.Command("/bin/bash", "-l")
		c.Dir = cwd
		c.Env = m.sb.Env("TERM=xterm-256color", "COLORTERM=truecolor", "LEARNBOX_SESSION="+id)
		return c
	}, func(c *exec.Cmd) error {
		var err error
		ptmx, err = pty.StartWithSize(c, &pty.Winsize{Cols: 100, Rows: 30})
		return err
	})
	if err != nil {
		return nil, err
	}
	s := &session{id: id, cmd: cmd, pty: ptmx, detached: time.Now()}
	m.sessions[id] = s
	m.log.Info("terminal started", "session", id, "pid", cmd.Process.Pid)
	go m.pump(s)
	return s, nil
}

// pump copies PTY output into the replay buffer and to the attached client
// until the shell exits.
func (m *Manager) pump(s *session) {
	chunk := make([]byte, 32<<10)
	for {
		n, err := s.pty.Read(chunk)
		if n > 0 {
			data := append([]byte(nil), chunk[:n]...)
			s.mu.Lock()
			s.buf = append(s.buf, data...)
			if over := len(s.buf) - replayBytes; over > 0 {
				s.buf = append([]byte(nil), s.buf[over:]...)
			}
			c := s.client
			s.mu.Unlock()
			if c != nil {
				c.send(frame{websocket.MessageBinary, data})
			}
		}
		if err != nil {
			break
		}
	}

	code := 0
	if err := s.cmd.Wait(); err != nil {
		var exitErr *exec.ExitError
		if errors.As(err, &exitErr) {
			code = exitErr.ExitCode()
		}
	}
	s.pty.Close()

	m.mu.Lock()
	if m.sessions[s.id] == s {
		delete(m.sessions, s.id)
	}
	m.mu.Unlock()

	s.mu.Lock()
	c := s.client
	s.mu.Unlock()
	if c != nil {
		msg, _ := json.Marshal(map[string]any{"type": "exit", "code": code})
		c.send(frame{websocket.MessageText, msg})
		// Give the writer a moment to flush the exit notice.
		time.AfterFunc(500*time.Millisecond, func() { c.close(websocket.StatusNormalClosure, "shell exited") })
	}
	m.log.Info("terminal exited", "session", s.id, "code", code)
}

// evictLocked makes room for a new session by killing the longest-detached
// ones. Attached sessions are never evicted.
func (m *Manager) evictLocked() {
	if len(m.sessions) < m.MaxSessions {
		return
	}
	var idle []*session
	for _, s := range m.sessions {
		s.mu.Lock()
		if s.client == nil {
			idle = append(idle, s)
		}
		s.mu.Unlock()
	}
	sort.Slice(idle, func(a, b int) bool { return idle[a].detached.Before(idle[b].detached) })
	for _, s := range idle {
		if len(m.sessions) < m.MaxSessions {
			break
		}
		m.killLocked(s, "evicted to make room")
	}
}

func (m *Manager) killLocked(s *session, why string) {
	delete(m.sessions, s.id)
	// The shell leads its own session (setsid), so -pid reaches everything
	// started from it that did not detach on purpose.
	syscall.Kill(-s.cmd.Process.Pid, syscall.SIGHUP)
	time.AfterFunc(2*time.Second, func() { syscall.Kill(-s.cmd.Process.Pid, syscall.SIGKILL) })
	m.log.Info("terminal killed", "session", s.id, "reason", why)
}

// Kill ends a session, e.g. when its lesson is reset.
func (m *Manager) Kill(id string) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if s := m.sessions[id]; s != nil {
		m.killLocked(s, "requested")
	}
}

// Janitor kills sessions that have been detached longer than IdleTimeout.
func (m *Manager) Janitor(ctx context.Context) {
	t := time.NewTicker(time.Minute)
	defer t.Stop()
	for {
		select {
		case <-ctx.Done():
			m.mu.Lock()
			for _, s := range m.sessions {
				m.killLocked(s, "shutdown")
			}
			m.mu.Unlock()
			return
		case <-t.C:
		}
		m.mu.Lock()
		for _, s := range m.sessions {
			s.mu.Lock()
			stale := s.client == nil && time.Since(s.detached) > m.IdleTimeout
			s.mu.Unlock()
			if stale {
				m.killLocked(s, "idle")
			}
		}
		m.mu.Unlock()
	}
}
