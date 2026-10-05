package httpapi

import (
	"encoding/json"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/profiles"
	"github.com/eiyanproject/learnbox/internal/sandbox"
	"github.com/eiyanproject/learnbox/internal/term"
	"github.com/eiyanproject/learnbox/internal/workspace"
)

func profileServer(t *testing.T) (http.Handler, *profiles.Registry) {
	t.Helper()
	reg, err := profiles.Open(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	sb := &sandbox.Sandbox{Home: t.TempDir()}
	ws, err := workspace.New(sb)
	if err != nil {
		t.Fatal(err)
	}
	h := New(Deps{
		Log:       slog.New(slog.DiscardHandler),
		WebDir:    t.TempDir(),
		Lib:       &content.Library{},
		Profiles:  reg,
		Workspace: ws,
		Terms:     term.NewManager(sb, slog.New(slog.DiscardHandler)),
	}).Handler()
	return h, reg
}

func do(t *testing.T, h http.Handler, method, url, body string, cookies ...*http.Cookie) *httptest.ResponseRecorder {
	t.Helper()
	r := httptest.NewRequest(method, url, strings.NewReader(body))
	r.Host = "localhost"
	if method != http.MethodGet {
		r.Header.Set("X-Learnbox", "1")
	}
	for _, c := range cookies {
		r.AddCookie(c)
	}
	w := httptest.NewRecorder()
	h.ServeHTTP(w, r)
	return w
}

func cookieFrom(w *httptest.ResponseRecorder) *http.Cookie {
	for _, c := range w.Result().Cookies() {
		if c.Name == profileCookie {
			return c
		}
	}
	return nil
}

func TestOneProfileNeedsNoChoice(t *testing.T) {
	h, _ := profileServer(t)
	if w := do(t, h, "GET", "/api/tracks", ""); w.Code != http.StatusOK {
		t.Fatalf("got %d: %s", w.Code, w.Body)
	}
}

func TestSeveralProfilesNeedAChoice(t *testing.T) {
	h, _ := profileServer(t)
	w := do(t, h, "POST", "/api/profiles", `{"name":"Ana"}`)
	if w.Code != http.StatusCreated {
		t.Fatalf("create: %d %s", w.Code, w.Body)
	}
	ana := cookieFrom(w)
	if ana == nil || ana.Value != "ana" || !ana.HttpOnly {
		t.Fatalf("create should select the new profile: %+v", ana)
	}

	w = do(t, h, "GET", "/api/tracks", "")
	if w.Code != http.StatusConflict || !strings.Contains(w.Body.String(), "choose_profile") {
		t.Fatalf("no cookie with two profiles: got %d %s", w.Code, w.Body)
	}
	if w := do(t, h, "GET", "/api/tracks", "", ana); w.Code != http.StatusOK {
		t.Fatalf("with cookie: %d", w.Code)
	}

	// A cookie naming something that is not a profile is ignored, not obeyed.
	bogus := &http.Cookie{Name: profileCookie, Value: "../etc"}
	if w := do(t, h, "GET", "/api/tracks", "", bogus); w.Code != http.StatusConflict {
		t.Fatalf("bogus cookie: %d", w.Code)
	}
}

func TestListShowsTheCurrentProfile(t *testing.T) {
	h, _ := profileServer(t)
	ana := cookieFrom(do(t, h, "POST", "/api/profiles", `{"name":"Ana"}`))
	var got struct {
		Profiles []profiles.Profile `json:"profiles"`
		Current  string             `json:"current"`
	}
	w := do(t, h, "GET", "/api/profiles", "", ana)
	if err := json.Unmarshal(w.Body.Bytes(), &got); err != nil {
		t.Fatal(err)
	}
	if len(got.Profiles) != 2 || got.Current != "ana" {
		t.Fatalf("got %+v", got)
	}
}

func TestSelectRenameDelete(t *testing.T) {
	h, reg := profileServer(t)
	do(t, h, "POST", "/api/profiles", `{"name":"Bo"}`)

	w := do(t, h, "POST", "/api/profiles/default/select", "")
	if c := cookieFrom(w); w.Code != http.StatusOK || c == nil || c.Value != "default" {
		t.Fatalf("select: %d %+v", w.Code, c)
	}
	if w := do(t, h, "POST", "/api/profiles/nobody/select", ""); w.Code != http.StatusNotFound {
		t.Fatalf("select unknown: %d", w.Code)
	}

	if w := do(t, h, "POST", "/api/profiles/default/rename", `{"name":"Me"}`); w.Code != http.StatusOK {
		t.Fatalf("rename: %d %s", w.Code, w.Body)
	}
	if p, _ := reg.Get("default"); p.Name != "Me" {
		t.Fatalf("rename not stored: %+v", p)
	}
	if w := do(t, h, "POST", "/api/profiles/default/rename", `{"name":"<b>"}`); w.Code != http.StatusBadRequest {
		t.Fatalf("bad name: %d", w.Code)
	}

	bo := &http.Cookie{Name: profileCookie, Value: "bo"}
	w = do(t, h, "DELETE", "/api/profiles/bo", "", bo)
	if w.Code != http.StatusOK {
		t.Fatalf("delete: %d %s", w.Code, w.Body)
	}
	if c := cookieFrom(w); c == nil || c.MaxAge >= 0 {
		t.Fatalf("deleting your own profile should clear the cookie: %+v", c)
	}
	if w := do(t, h, "DELETE", "/api/profiles/default", ""); w.Code != http.StatusBadRequest {
		t.Fatalf("deleting the last profile: %d", w.Code)
	}
}

func TestProfileChangesNeedTheHeader(t *testing.T) {
	h, _ := profileServer(t)
	r := httptest.NewRequest("POST", "/api/profiles", strings.NewReader(`{"name":"X"}`))
	r.Host = "localhost"
	w := httptest.NewRecorder()
	h.ServeHTTP(w, r)
	if w.Code != http.StatusForbidden {
		t.Fatalf("cross-site create should be refused: %d", w.Code)
	}
}

func TestTerminalRefusesTheServersOwnPrefix(t *testing.T) {
	h, _ := profileServer(t)
	if w := do(t, h, "GET", "/api/term?session=profile/ana/scratch", ""); w.Code != http.StatusBadRequest {
		t.Fatalf("got %d", w.Code)
	}
}
