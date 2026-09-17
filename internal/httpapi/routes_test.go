package httpapi

import (
	"net/http"
	"testing"
)

// The mux panics at registration on conflicting patterns; catch that in CI
// rather than at service start.
func TestRoutesRegister(t *testing.T) {
	s := &Server{Deps: Deps{WebDir: t.TempDir()}, mux: http.NewServeMux()}
	s.routes()
}
