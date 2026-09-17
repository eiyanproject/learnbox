package access

import (
	"context"
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"math/big"
	"net/http"
	"net/http/httptest"
	"sync/atomic"
	"testing"
	"time"
)

const team = "example.cloudflareaccess.com"
const aud = "aud-tag-123"

type fixture struct {
	key     *rsa.PrivateKey
	kid     string
	fetches atomic.Int32
	srv     *httptest.Server
	v       *Verifier
	now     time.Time
}

func newFixture(t *testing.T) *fixture {
	t.Helper()
	key, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		t.Fatal(err)
	}
	f := &fixture{key: key, kid: "k1", now: time.Unix(1_800_000_000, 0)}
	f.srv = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		f.fetches.Add(1)
		json.NewEncoder(w).Encode(map[string]any{"keys": []map[string]string{{
			"kid": f.kid, "kty": "RSA", "alg": "RS256",
			"n": base64.RawURLEncoding.EncodeToString(key.N.Bytes()),
			"e": base64.RawURLEncoding.EncodeToString(big.NewInt(int64(key.E)).Bytes()),
		}}})
	}))
	t.Cleanup(f.srv.Close)
	f.v = NewVerifier("https://"+team+"/", aud)
	f.v.CertsURL = f.srv.URL
	f.v.Now = func() time.Time { return f.now }
	return f
}

func (f *fixture) token(t *testing.T, alg string, claims map[string]any) string {
	t.Helper()
	seg := func(v any) string {
		raw, _ := json.Marshal(v)
		return base64.RawURLEncoding.EncodeToString(raw)
	}
	signing := seg(map[string]string{"alg": alg, "kid": f.kid}) + "." + seg(claims)
	digest := sha256.Sum256([]byte(signing))
	sig, err := rsa.SignPKCS1v15(rand.Reader, f.key, crypto.SHA256, digest[:])
	if err != nil {
		t.Fatal(err)
	}
	return signing + "." + base64.RawURLEncoding.EncodeToString(sig)
}

func (f *fixture) good() map[string]any {
	return map[string]any{
		"aud":   []string{aud},
		"iss":   "https://" + team,
		"exp":   f.now.Add(time.Hour).Unix(),
		"email": "owner@example.com",
	}
}

func TestValidToken(t *testing.T) {
	f := newFixture(t)
	email, err := f.v.Verify(context.Background(), f.token(t, "RS256", f.good()))
	if err != nil || email != "owner@example.com" {
		t.Fatalf("got %q, %v", email, err)
	}
}

func TestAudienceAsString(t *testing.T) {
	f := newFixture(t)
	c := f.good()
	c["aud"] = aud
	if _, err := f.v.Verify(context.Background(), f.token(t, "RS256", c)); err != nil {
		t.Fatal(err)
	}
}

func TestRejections(t *testing.T) {
	f := newFixture(t)
	cases := map[string]func(map[string]any){
		"expired":        func(c map[string]any) { c["exp"] = f.now.Add(-2 * time.Minute).Unix() },
		"no exp":         func(c map[string]any) { delete(c, "exp") },
		"wrong audience": func(c map[string]any) { c["aud"] = []string{"someone-else"} },
		"wrong issuer":   func(c map[string]any) { c["iss"] = "https://evil.cloudflareaccess.com" },
		"not yet valid":  func(c map[string]any) { c["nbf"] = f.now.Add(10 * time.Minute).Unix() },
	}
	for name, mutate := range cases {
		c := f.good()
		mutate(c)
		if _, err := f.v.Verify(context.Background(), f.token(t, "RS256", c)); !errors.Is(err, ErrInvalidToken) {
			t.Errorf("%s: want ErrInvalidToken, got %v", name, err)
		}
	}
}

func TestTamperedAndMalformed(t *testing.T) {
	f := newFixture(t)
	tok := f.token(t, "RS256", f.good())
	other := f.good()
	other["email"] = "attacker@example.com"
	forged := f.token(t, "RS256", other)
	spliced := tok[:len(tok)-len(tok[len(tok)-10:])] + forged[len(forged)-10:]
	for name, bad := range map[string]string{
		"spliced signature": spliced,
		"two segments":      "a.b",
		"garbage":           "not-a-token",
		"alg none":          f.token(t, "none", f.good()),
	} {
		if _, err := f.v.Verify(context.Background(), bad); err == nil {
			t.Errorf("%s: accepted", name)
		}
	}
	if _, err := f.v.Verify(context.Background(), ""); !errors.Is(err, ErrNoToken) {
		t.Errorf("empty token: %v", err)
	}
}

func TestKeysAreCached(t *testing.T) {
	f := newFixture(t)
	tok := f.token(t, "RS256", f.good())
	for range 5 {
		if _, err := f.v.Verify(context.Background(), tok); err != nil {
			t.Fatal(err)
		}
	}
	if n := f.fetches.Load(); n != 1 {
		t.Fatalf("fetched keys %d times", n)
	}
}

func TestTokenFromHeaderOrCookie(t *testing.T) {
	r := httptest.NewRequest("GET", "/", nil)
	r.AddCookie(&http.Cookie{Name: CookieName, Value: "from-cookie"})
	if TokenFrom(r) != "from-cookie" {
		t.Fatal("cookie fallback")
	}
	r.Header.Set(HeaderName, "from-header")
	if TokenFrom(r) != "from-header" {
		t.Fatal("header wins")
	}
}
