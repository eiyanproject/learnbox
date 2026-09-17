package httpapi

import (
	"log/slog"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/eiyanproject/learnbox/internal/access"
)

func server(t *testing.T, accessHosts []string, v *access.Verifier) http.Handler {
	t.Helper()
	return New(Deps{
		Log:         slog.New(slog.DiscardHandler),
		WebDir:      t.TempDir(),
		AccessHosts: accessHosts,
		Access:      v,
	}).Handler()
}

func status(t *testing.T, h http.Handler, host string) int {
	t.Helper()
	r := httptest.NewRequest(http.MethodGet, "/healthz", nil)
	r.Host = host
	w := httptest.NewRecorder()
	h.ServeHTTP(w, r)
	return w.Code
}

func TestAccessHostFailsClosedWithoutVerifier(t *testing.T) {
	h := server(t, []string{"learnbox.example.com"}, nil)
	if code := status(t, h, "learnbox.example.com"); code != http.StatusServiceUnavailable {
		t.Errorf("public host without Access configured: got %d, want 503", code)
	}
}

func TestAccessHostRequiresToken(t *testing.T) {
	h := server(t, []string{"learnbox.example.com"}, access.NewVerifier("team.cloudflareaccess.com", "aud"))
	if code := status(t, h, "learnbox.example.com"); code != http.StatusForbidden {
		t.Errorf("public host without a token: got %d, want 403", code)
	}
}

func TestLanHostsAreNotGated(t *testing.T) {
	h := server(t, []string{"learnbox.example.com"}, nil)
	for _, host := range []string{"192.168.0.116:8080", "localhost:8080"} {
		if code := status(t, h, host); code != http.StatusOK {
			t.Errorf("%s: got %d, want 200", host, code)
		}
	}
}

func TestUnknownHostIsRefused(t *testing.T) {
	h := server(t, nil, nil)
	if code := status(t, h, "evil.example.com"); code != http.StatusMisdirectedRequest {
		t.Errorf("unknown host: got %d, want 421", code)
	}
}
