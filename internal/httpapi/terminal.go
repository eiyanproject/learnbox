package httpapi

import (
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/coder/websocket"

	"github.com/eiyanproject/learnbox/internal/term"
)

// terminal upgrades to a WebSocket attached to a shell session.
//
//	/api/term?session=scratch                       shell in ~
//	/api/term?session=lesson/python/learn/01-hello  shell in that lesson's workspace
//
// A session id starting with "lesson/" is bound to that lesson's workspace;
// anything else starts in the learner's home.
func (s *Server) terminal(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("session")
	if !term.ValidID(id) {
		writeErr(w, http.StatusBadRequest, "bad session id")
		return
	}
	// Refuse before the upgrade: an error here is a readable HTTP response,
	// whereas a socket that opens and immediately dies tells the learner nothing.
	if err := s.diskHeadroom(); err != nil {
		s.errs.WithLabelValues("disk_full").Inc()
		writeErr(w, http.StatusInsufficientStorage, err.Error())
		return
	}
	cwd := s.Sandbox.Home
	if lessonID, ok := strings.CutPrefix(id, "lesson/"); ok {
		l := s.Lib.Lesson(lessonID)
		if l == nil {
			writeErr(w, http.StatusNotFound, "no such lesson")
			return
		}
		dir, err := s.Workspace.Ensure(l)
		if err != nil {
			s.fail(w, "workspace", err)
			return
		}
		cwd = dir
	}

	// Default options check Origin against Host, so another site cannot open
	// this socket from the learner's browser.
	conn, err := websocket.Accept(w, r, nil)
	if err != nil {
		s.errs.WithLabelValues("ws_accept").Inc()
		return
	}
	if err := s.Terms.Attach(r.Context(), id, cwd, conn); err != nil {
		s.errs.WithLabelValues("terminal").Inc()
		s.Log.Error("terminal attach failed", "session", id, "err", err.Error())
	}
}

// static serves the built frontend, falling back to index.html so client-side
// routes survive a reload.
func (s *Server) static() http.Handler {
	files := http.FileServer(http.Dir(s.WebDir))
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Registered without a method so it does not conflict with "/api/".
		if r.Method != http.MethodGet && r.Method != http.MethodHead {
			writeErr(w, http.StatusMethodNotAllowed, "method not allowed")
			return
		}
		p := filepath.Join(s.WebDir, filepath.FromSlash(filepath.Clean("/"+r.URL.Path)))
		if st, err := os.Stat(p); err != nil || st.IsDir() {
			w.Header().Set("Cache-Control", "no-cache")
			http.ServeFile(w, r, filepath.Join(s.WebDir, "index.html"))
			return
		}
		if strings.HasPrefix(r.URL.Path, "/assets/") {
			w.Header().Set("Cache-Control", "public, max-age=31536000, immutable")
		}
		files.ServeHTTP(w, r)
	})
}
