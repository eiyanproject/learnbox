// Package workspace manages the learner's editable copy of each lesson under
// ~/learn/<lang>/<section>/<slug>.
//
// The service runs as root but everything here lives in a directory the
// learner owns, so a symlink planted there (say ~/learn/python -> /etc) must
// not turn a save into a root write elsewhere. All access goes through an
// os.Root anchored at the learner's home, which refuses any path that
// resolves outside it.
package workspace

import (
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path"
	"path/filepath"
	"slices"
	"strings"
	"syscall"
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
	"github.com/eiyanproject/learnbox/internal/sandbox"
)

var ErrNotAllowed = errors.New("file is not part of this lesson")

type Manager struct {
	home *os.Root
	sb   *sandbox.Sandbox
}

func New(sb *sandbox.Sandbox) (*Manager, error) {
	home, err := os.OpenRoot(sb.Home)
	if err != nil {
		return nil, err
	}
	return &Manager{home: home, sb: sb}, nil
}

// Rel is the workspace path relative to the learner's home.
func (m *Manager) Rel(l *content.Lesson) string {
	return path.Join("learn", l.Lang, l.Section, l.Slug)
}

// Dir is the absolute workspace path, for use as a process working directory.
func (m *Manager) Dir(l *content.Lesson) string {
	return filepath.Join(m.sb.Home, filepath.FromSlash(m.Rel(l)))
}

// Ensure creates the workspace from the starter files the first time a lesson
// is opened. Existing workspaces are left exactly as the learner left them.
func (m *Manager) Ensure(l *content.Lesson) (string, error) {
	rel := m.Rel(l)
	if _, err := m.home.Stat(rel); err == nil {
		return m.Dir(l), nil
	}
	if err := m.MkdirAll(path.Dir(rel)); err != nil {
		return "", err
	}
	tmp := rel + ".creating"
	if err := m.home.RemoveAll(tmp); err != nil {
		return "", err
	}
	if err := m.MkdirAll(tmp); err != nil {
		return "", err
	}
	if err := m.CopyIn(l.StarterDir(), tmp); err != nil && !os.IsNotExist(err) {
		return "", err
	}
	return m.Dir(l), m.home.Rename(tmp, rel)
}

// Reset moves the current workspace aside (not deleted: a reset is one
// misclick away) and recreates it from the starter files.
func (m *Manager) Reset(l *content.Lesson) (backup string, err error) {
	rel := m.Rel(l)
	if _, err := m.home.Stat(rel); err == nil {
		if err := m.MkdirAll("learn/.reset-backups"); err != nil {
			return "", err
		}
		backup = path.Join("learn/.reset-backups",
			fmt.Sprintf("%s-%s-%s-%s", l.Lang, l.Section, l.Slug, time.Now().Format("20060102-150405")))
		if err := m.home.Rename(rel, backup); err != nil {
			return "", err
		}
	}
	_, err = m.Ensure(l)
	return backup, err
}

type File struct {
	Name    string `json:"name"`
	Content string `json:"content"`
	MTime   int64  `json:"mtime"` // unix ms
	Missing bool   `json:"missing,omitempty"`
}

func (m *Manager) file(l *content.Lesson, name string) (string, error) {
	if !slices.Contains(l.Files, name) {
		return "", ErrNotAllowed
	}
	return path.Join(m.Rel(l), name), nil
}

func (m *Manager) Read(l *content.Lesson, name string) (File, error) {
	rel, err := m.file(l, name)
	if err != nil {
		return File{}, err
	}
	raw, err := m.home.ReadFile(rel)
	if errors.Is(err, fs.ErrNotExist) {
		return File{Name: name, Missing: true}, nil
	}
	if err != nil {
		return File{}, err
	}
	st, err := m.home.Stat(rel)
	if err != nil {
		return File{}, err
	}
	return File{Name: name, Content: string(raw), MTime: st.ModTime().UnixMilli()}, nil
}

func (m *Manager) MTimes(l *content.Lesson) map[string]int64 {
	out := map[string]int64{}
	for _, name := range l.Files {
		out[name] = 0
		if st, err := m.home.Stat(path.Join(m.Rel(l), name)); err == nil {
			out[name] = st.ModTime().UnixMilli()
		}
	}
	return out
}

// Write replaces a file atomically, keeping it owned by the learner.
func (m *Manager) Write(l *content.Lesson, name, body string) (int64, error) {
	rel, err := m.file(l, name)
	if err != nil {
		return 0, err
	}
	if err := m.MkdirAll(path.Dir(rel)); err != nil {
		return 0, err
	}
	tmp := rel + ".learnbox-tmp"
	if err := m.writeFile(tmp, []byte(body)); err != nil {
		return 0, err
	}
	if err := m.home.Rename(tmp, rel); err != nil {
		m.home.Remove(tmp)
		return 0, err
	}
	st, err := m.home.Stat(rel)
	if err != nil {
		return 0, err
	}
	return st.ModTime().UnixMilli(), nil
}

// MkdirAll creates rel (relative to home) and any missing parents, each owned
// by the learner.
func (m *Manager) MkdirAll(rel string) error {
	if rel == "." || rel == "" {
		return nil
	}
	if st, err := m.home.Stat(rel); err == nil {
		if !st.IsDir() {
			return fmt.Errorf("%s exists and is not a directory", rel)
		}
		return nil
	}
	if err := m.MkdirAll(path.Dir(rel)); err != nil {
		return err
	}
	if err := m.home.Mkdir(rel, 0o755); err != nil && !errors.Is(err, fs.ErrExist) {
		return err
	}
	return m.chown(rel)
}

// ReadFileRel reads a file relative to the learner's home.
func (m *Manager) ReadFileRel(rel string) ([]byte, error) { return m.home.ReadFile(rel) }

// RemoveAll removes rel (relative to home).
func (m *Manager) RemoveAll(rel string) error { return m.home.RemoveAll(rel) }

// CopyIn copies a directory tree from outside the learner's home (lesson
// starter or test files) to rel inside it.
func (m *Manager) CopyIn(src, rel string) error {
	if _, err := os.Stat(src); err != nil {
		return err
	}
	return filepath.WalkDir(src, func(p string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		sub, _ := filepath.Rel(src, p)
		target := path.Join(rel, filepath.ToSlash(sub))
		if d.IsDir() {
			return m.MkdirAll(target)
		}
		if !d.Type().IsRegular() {
			return nil
		}
		raw, err := os.ReadFile(p)
		if err != nil {
			return err
		}
		return m.writeFile(target, raw)
	})
}

// CopyWithin copies a tree from one place in the learner's home to another,
// skipping build output. Symlinks are not followed.
func (m *Manager) CopyWithin(srcRel, dstRel string) error {
	return fs.WalkDir(m.home.FS(), srcRel, func(p string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		sub := p[len(srcRel):]
		target := dstRel + sub
		if d.IsDir() {
			if name := d.Name(); p != srcRel && (name == "target" || name == "__pycache__" || name == ".pytest_cache") {
				return fs.SkipDir
			}
			return m.MkdirAll(target)
		}
		if !d.Type().IsRegular() {
			return nil
		}
		raw, err := m.home.ReadFile(p)
		if err != nil {
			return err
		}
		return m.writeFile(target, raw)
	})
}

func (m *Manager) writeFile(rel string, data []byte) error {
	m.home.Remove(rel) // never write through an existing symlink or hard link
	f, err := m.home.OpenFile(rel, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	if _, err := f.Write(data); err != nil {
		f.Close()
		return err
	}
	if err := f.Close(); err != nil {
		return err
	}
	return m.chown(rel)
}

func (m *Manager) chown(rel string) error {
	if os.Geteuid() != 0 {
		return nil
	}
	return m.home.Lchown(rel, m.sb.UID, m.sb.GID)
}

// FreeBytes reports the space left on the filesystem holding the learner's
// home. A workspace that fills the disk does not fail loudly: writes start
// failing everywhere at once, including the progress file, so the service
// checks this before starting anything new rather than after.
func (m *Manager) FreeBytes() (int64, error) {
	var st syscall.Statfs_t
	if err := syscall.Statfs(m.sb.Home, &st); err != nil {
		return 0, err
	}
	return int64(st.Bavail) * int64(st.Bsize), nil
}

// ListRel returns the names of files directly inside rel whose name ends with
// suffix. Used by the Java checker, which has to hand javac an explicit file
// list: the runner starts processes directly rather than through a shell, so
// there is nothing to expand a "*.java" glob.
func (m *Manager) ListRel(rel, suffix string) ([]string, error) {
	entries, err := fs.ReadDir(m.home.FS(), rel)
	if err != nil {
		return nil, err
	}
	var names []string
	for _, e := range entries {
		if !e.IsDir() && strings.HasSuffix(e.Name(), suffix) {
			names = append(names, e.Name())
		}
	}
	slices.Sort(names)
	return names, nil
}
