package profiles

import (
	"os"
	"path/filepath"
	"testing"
)

func TestFirstOpenCreatesTheDefaultProfile(t *testing.T) {
	r, err := Open(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	ps := r.List()
	if len(ps) != 1 || ps[0].ID != DefaultID {
		t.Fatalf("got %+v", ps)
	}
}

func TestDefaultKeepsTheOldProgressFileAndFolder(t *testing.T) {
	dir := t.TempDir()
	r, _ := Open(dir)
	if r.progressPath(DefaultID) != filepath.Join(dir, "progress.json") {
		t.Fatalf("default progress moved: %s", r.progressPath(DefaultID))
	}
	if WorkspaceBase(DefaultID) != "learn" || WorkspaceBase("ana") != "profiles/ana/learn" {
		t.Fatal("workspace bases changed")
	}
}

func TestCreateMakesUniqueSafeIDs(t *testing.T) {
	r, _ := Open(t.TempDir())
	a, err := r.Create("  Ana   Lopez ")
	if err != nil {
		t.Fatal(err)
	}
	b, _ := r.Create("ana lopez")
	c, _ := r.Create("Default")
	d, _ := r.Create("Ébène")
	if a.ID != "ana-lopez" || b.ID != "ana-lopez-2" || c.ID != "player" || d.ID != "b-ne" {
		t.Fatalf("ids: %q %q %q %q", a.ID, b.ID, c.ID, d.ID)
	}
	if a.Name != "Ana Lopez" {
		t.Fatalf("name not tidied: %q", a.Name)
	}
	for _, p := range []Profile{a, b, c, d} {
		if !ValidID(p.ID) {
			t.Fatalf("invalid id %q", p.ID)
		}
	}
}

func TestBadNamesAreRefused(t *testing.T) {
	r, _ := Open(t.TempDir())
	for _, n := range []string{"", "   ", "a/b", "<script>", "this name is far too long to be anybody's name ok"} {
		if _, err := r.Create(n); err == nil {
			t.Errorf("accepted %q", n)
		}
	}
}

func TestValidIDRejectsPaths(t *testing.T) {
	for _, id := range []string{"../x", "a/b", "", "A", "-x", ".hidden"} {
		if ValidID(id) {
			t.Errorf("accepted %q", id)
		}
	}
}

func TestDeleteRemovesProgressButNotTheLastProfile(t *testing.T) {
	dir := t.TempDir()
	r, _ := Open(dir)
	if err := r.Delete(DefaultID); err != ErrLastOne {
		t.Fatalf("got %v", err)
	}
	p, _ := r.Create("Bo")
	s, err := r.Progress(p.ID)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := s.Opened("python/learn/01"); err != nil {
		t.Fatal(err)
	}
	file := filepath.Join(dir, "progress-bo.json")
	if _, err := os.Stat(file); err != nil {
		t.Fatal("progress file not written")
	}
	if err := r.Delete(p.ID); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(file); !os.IsNotExist(err) {
		t.Fatal("progress file left behind")
	}
	if _, ok := r.Get(p.ID); ok {
		t.Fatal("profile still listed")
	}
}

func TestProfilesSurviveReopen(t *testing.T) {
	dir := t.TempDir()
	r, _ := Open(dir)
	r.Create("Cy")
	r.Rename(DefaultID, "Me")
	r2, err := Open(dir)
	if err != nil {
		t.Fatal(err)
	}
	ps := r2.List()
	if len(ps) != 2 || ps[0].Name != "Me" || ps[1].ID != "cy" {
		t.Fatalf("got %+v", ps)
	}
}

func TestDataFilesFollowTheProfile(t *testing.T) {
	dir := t.TempDir()
	r, _ := Open(dir)
	r.AlsoDelete("quiz")
	if r.DataFile(DefaultID, "quiz") != filepath.Join(dir, "quiz.json") {
		t.Fatal("default data file")
	}
	p, _ := r.Create("Cy")
	f := r.DataFile(p.ID, "quiz")
	if f != filepath.Join(dir, "quiz-cy.json") {
		t.Fatalf("got %s", f)
	}
	if err := os.WriteFile(f, []byte("{}"), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := r.Delete(p.ID); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(f); !os.IsNotExist(err) {
		t.Fatal("quiz file left behind")
	}
}
