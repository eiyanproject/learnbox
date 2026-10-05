package httpapi

import (
	"encoding/json"
	"errors"
	"net/http"
	"path"
	"strings"
	"time"

	"github.com/eiyanproject/learnbox/internal/profiles"
	"github.com/eiyanproject/learnbox/internal/progress"
	"github.com/eiyanproject/learnbox/internal/workspace"
)

// profileCookie names the profile a browser has picked. It is a preference,
// not a credential: profiles separate progress for people sharing the box,
// and anyone who can reach the box can pick any of them.
const profileCookie = "learnbox_profile"

// viewer is the profile a request acts for, with its own progress and files.
type viewer struct {
	ID       string
	Name     string
	Progress *progress.Store
	WS       *workspace.Manager
}

// currentProfile resolves the request's profile: the one its cookie names, or
// the only one there is. ok is false when there are several and none is
// picked - the frontend then shows the picker.
func (s *Server) currentProfile(r *http.Request) (profiles.Profile, bool) {
	if c, err := r.Cookie(profileCookie); err == nil && profiles.ValidID(c.Value) {
		if p, ok := s.Profiles.Get(c.Value); ok {
			return p, true
		}
	}
	if all := s.Profiles.List(); len(all) == 1 {
		return all[0], true
	}
	return profiles.Profile{}, false
}

// who returns the request's viewer, or writes 409 "choose_profile" and
// returns nil.
func (s *Server) who(w http.ResponseWriter, r *http.Request) *viewer {
	p, ok := s.currentProfile(r)
	if !ok {
		writeJSON(w, http.StatusConflict, map[string]string{"error": "choose a profile first", "code": "choose_profile"})
		return nil
	}
	store, err := s.Profiles.Progress(p.ID)
	if err != nil {
		s.fail(w, "progress", err)
		return nil
	}
	return &viewer{ID: p.ID, Name: p.Name, Progress: store, WS: s.Workspace.For(profiles.WorkspaceBase(p.ID))}
}

// sessionKey keeps one profile's terminals apart from another's. The default
// profile keeps the bare ids it always had.
func (v *viewer) sessionKey(id string) string {
	if v.ID == profiles.DefaultID {
		return id
	}
	return "profile/" + v.ID + "/" + id
}

// home is where the profile's free terminal starts.
func (v *viewer) home() string {
	if v.ID == profiles.DefaultID {
		return ""
	}
	return path.Join("profiles", v.ID)
}

func (s *Server) setProfileCookie(w http.ResponseWriter, r *http.Request, id string) {
	c := &http.Cookie{
		Name:     profileCookie,
		Value:    id,
		Path:     "/",
		HttpOnly: true,
		SameSite: http.SameSiteLaxMode,
		// Public hostnames are https behind Cloudflare; LAN access is plain
		// http, where a Secure cookie would simply never come back.
		Secure:  s.accessHosts[hostOnly(r.Host)],
		Expires: time.Now().AddDate(1, 0, 0),
	}
	if id == "" {
		c.Expires = time.Unix(0, 0)
		c.MaxAge = -1
	}
	http.SetCookie(w, c)
}

// ---------- endpoints ----------

func (s *Server) listProfiles(w http.ResponseWriter, r *http.Request) {
	cur, ok := s.currentProfile(r)
	current := ""
	if ok {
		current = cur.ID
	}
	writeJSON(w, http.StatusOK, map[string]any{"profiles": s.Profiles.List(), "current": current})
}

func readName(w http.ResponseWriter, r *http.Request) (string, bool) {
	var body struct {
		Name string `json:"name"`
	}
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 4<<10)).Decode(&body); err != nil {
		writeErr(w, http.StatusBadRequest, "body must be {\"name\": string}")
		return "", false
	}
	return body.Name, true
}

func (s *Server) profileErr(w http.ResponseWriter, err error) {
	switch {
	case errors.Is(err, profiles.ErrNotFound):
		writeErr(w, http.StatusNotFound, err.Error())
	case errors.Is(err, profiles.ErrBadName), errors.Is(err, profiles.ErrTooMany), errors.Is(err, profiles.ErrLastOne):
		writeErr(w, http.StatusBadRequest, err.Error())
	default:
		s.fail(w, "profiles", err)
	}
}

func (s *Server) createProfile(w http.ResponseWriter, r *http.Request) {
	name, ok := readName(w, r)
	if !ok {
		return
	}
	p, err := s.Profiles.Create(name)
	if err != nil {
		s.profileErr(w, err)
		return
	}
	s.setProfileCookie(w, r, p.ID)
	s.Log.Info("profile created", "profile", p.ID)
	writeJSON(w, http.StatusCreated, p)
}

func (s *Server) selectProfile(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	p, ok := s.Profiles.Get(id)
	if !profiles.ValidID(id) || !ok {
		writeErr(w, http.StatusNotFound, profiles.ErrNotFound.Error())
		return
	}
	s.setProfileCookie(w, r, p.ID)
	writeJSON(w, http.StatusOK, p)
}

func (s *Server) renameProfile(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if !profiles.ValidID(id) {
		writeErr(w, http.StatusNotFound, profiles.ErrNotFound.Error())
		return
	}
	name, ok := readName(w, r)
	if !ok {
		return
	}
	p, err := s.Profiles.Rename(id, name)
	if err != nil {
		s.profileErr(w, err)
		return
	}
	writeJSON(w, http.StatusOK, p)
}

func (s *Server) deleteProfile(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	if !profiles.ValidID(id) {
		writeErr(w, http.StatusNotFound, profiles.ErrNotFound.Error())
		return
	}
	if err := s.Profiles.Delete(id); err != nil {
		s.profileErr(w, err)
		return
	}
	s.Terms.KillPrefix("profile/" + id + "/")
	if c, err := r.Cookie(profileCookie); err == nil && c.Value == id {
		s.setProfileCookie(w, r, "")
	}
	s.Log.Info("profile deleted", "profile", id)
	writeJSON(w, http.StatusOK, map[string]string{
		"status": "deleted",
		"files":  "~/" + strings.TrimSuffix(profiles.WorkspaceBase(id), "/learn") + " (kept)",
	})
}
