package httpapi

import (
	"log/slog"
	"os/user"
	"strings"
	"testing"

	"github.com/eiyanproject/learnbox/internal/sandbox"
	"github.com/eiyanproject/learnbox/internal/workspace"
)

func testWorkspace(t *testing.T) *workspace.Manager {
	t.Helper()
	// A sandbox with no limits does not touch cgroups, so this works as an
	// ordinary test user.
	sb, err := sandbox.New(currentUser(t), sandbox.Limits{}, slog.New(slog.DiscardHandler))
	if err != nil {
		t.Skipf("cannot build a sandbox for the current user: %v", err)
	}
	sb.Home = t.TempDir()
	ws, err := workspace.New(sb)
	if err != nil {
		t.Skipf("cannot open workspace: %v", err)
	}
	return ws
}

func TestDiskHeadroomDisabledWhenUnset(t *testing.T) {
	s := &Server{Deps: Deps{Workspace: testWorkspace(t), MinFreeDisk: 0}}
	if err := s.diskHeadroom(); err != nil {
		t.Fatalf("MinFreeDisk=0 should disable the check, got %v", err)
	}
}

func TestDiskHeadroomAllowsWhenThereIsSpace(t *testing.T) {
	s := &Server{Deps: Deps{Workspace: testWorkspace(t), MinFreeDisk: 1}}
	if err := s.diskHeadroom(); err != nil {
		t.Fatalf("one byte of headroom should pass, got %v", err)
	}
}

func TestDiskHeadroomRefusesWhenBelowTheFloor(t *testing.T) {
	// A floor no filesystem can satisfy: 1 EiB.
	s := &Server{Deps: Deps{Workspace: testWorkspace(t), MinFreeDisk: 1 << 60}}
	err := s.diskHeadroom()
	if err == nil {
		t.Fatal("expected a refusal when free space is below the floor")
	}
	// The message has to say what to do about it, not just that it failed.
	for _, want := range []string{"free in the workspace", "/home/learner"} {
		if !strings.Contains(err.Error(), want) {
			t.Errorf("message %q should mention %q", err, want)
		}
	}
}

func currentUser(t *testing.T) string {
	t.Helper()
	u, err := user.Current()
	if err != nil {
		t.Skipf("cannot determine current user: %v", err)
	}
	return u.Username
}
