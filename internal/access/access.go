// Package access verifies Cloudflare Access tokens, so a public hostname is
// protected by the app itself and not only by the edge configuration.
//
// Cloudflare Access signs every request it lets through with an RS256 JWT in
// the Cf-Access-Jwt-Assertion header (and the CF_Authorization cookie). The
// signing keys are published at https://<team>.cloudflareaccess.com/cdn-cgi/access/certs.
// If the Access application is ever deleted or bypassed, requests arrive
// without a valid token and are refused here.
package access

import (
	"context"
	"crypto"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"math/big"
	"net/http"
	"slices"
	"strings"
	"sync"
	"time"
)

const (
	HeaderName = "Cf-Access-Jwt-Assertion"
	CookieName = "CF_Authorization"
	leeway     = time.Minute
	keysMaxAge = time.Hour
)

var (
	ErrNoToken      = errors.New("no Cloudflare Access token")
	ErrInvalidToken = errors.New("invalid Cloudflare Access token")
)

type Verifier struct {
	TeamDomain string // e.g. "myteam.cloudflareaccess.com"
	Audience   string // the Access application's AUD tag
	CertsURL   string // defaults to https://<TeamDomain>/cdn-cgi/access/certs
	Client     *http.Client
	Now        func() time.Time

	mu      sync.Mutex
	keys    map[string]*rsa.PublicKey
	fetched time.Time
}

func NewVerifier(teamDomain, audience string) *Verifier {
	teamDomain = strings.TrimSuffix(strings.TrimPrefix(strings.TrimSpace(teamDomain), "https://"), "/")
	return &Verifier{
		TeamDomain: teamDomain,
		Audience:   strings.TrimSpace(audience),
		CertsURL:   "https://" + teamDomain + "/cdn-cgi/access/certs",
		Client:     &http.Client{Timeout: 10 * time.Second},
		Now:        time.Now,
	}
}

// TokenFrom extracts the token from the header, or the cookie as a fallback.
func TokenFrom(r *http.Request) string {
	if t := r.Header.Get(HeaderName); t != "" {
		return t
	}
	if c, err := r.Cookie(CookieName); err == nil {
		return c.Value
	}
	return ""
}

type header struct {
	Alg string `json:"alg"`
	Kid string `json:"kid"`
}

type claims struct {
	Aud   audience `json:"aud"`
	Iss   string   `json:"iss"`
	Exp   int64    `json:"exp"`
	Nbf   int64    `json:"nbf"`
	Email string   `json:"email"`
}

// audience accepts both a string and an array of strings, as JWTs allow.
type audience []string

func (a *audience) UnmarshalJSON(b []byte) error {
	var one string
	if json.Unmarshal(b, &one) == nil {
		*a = []string{one}
		return nil
	}
	var many []string
	if err := json.Unmarshal(b, &many); err != nil {
		return err
	}
	*a = many
	return nil
}

// Verify checks signature, audience, issuer and expiry, and returns the
// authenticated email.
func (v *Verifier) Verify(ctx context.Context, token string) (string, error) {
	if token == "" {
		return "", ErrNoToken
	}
	parts := strings.Split(token, ".")
	if len(parts) != 3 {
		return "", fmt.Errorf("%w: malformed", ErrInvalidToken)
	}
	var h header
	if err := decodeSegment(parts[0], &h); err != nil {
		return "", fmt.Errorf("%w: header: %v", ErrInvalidToken, err)
	}
	if h.Alg != "RS256" {
		return "", fmt.Errorf("%w: unexpected alg %q", ErrInvalidToken, h.Alg)
	}
	key, err := v.key(ctx, h.Kid)
	if err != nil {
		return "", err
	}
	sig, err := base64.RawURLEncoding.DecodeString(parts[2])
	if err != nil {
		return "", fmt.Errorf("%w: signature encoding", ErrInvalidToken)
	}
	digest := sha256.Sum256([]byte(parts[0] + "." + parts[1]))
	if err := rsa.VerifyPKCS1v15(key, crypto.SHA256, digest[:], sig); err != nil {
		return "", fmt.Errorf("%w: bad signature", ErrInvalidToken)
	}

	var c claims
	if err := decodeSegment(parts[1], &c); err != nil {
		return "", fmt.Errorf("%w: claims: %v", ErrInvalidToken, err)
	}
	now := v.Now()
	if c.Exp == 0 || now.After(time.Unix(c.Exp, 0).Add(leeway)) {
		return "", fmt.Errorf("%w: expired", ErrInvalidToken)
	}
	if c.Nbf != 0 && now.Add(leeway).Before(time.Unix(c.Nbf, 0)) {
		return "", fmt.Errorf("%w: not yet valid", ErrInvalidToken)
	}
	if !slices.Contains(c.Aud, v.Audience) {
		return "", fmt.Errorf("%w: wrong audience", ErrInvalidToken)
	}
	if c.Iss != "https://"+v.TeamDomain {
		return "", fmt.Errorf("%w: wrong issuer %q", ErrInvalidToken, c.Iss)
	}
	return c.Email, nil
}

func decodeSegment(seg string, into any) error {
	raw, err := base64.RawURLEncoding.DecodeString(seg)
	if err != nil {
		return err
	}
	return json.Unmarshal(raw, into)
}

// key returns the signing key for kid, refreshing the key set when it is
// stale or the kid is unknown (Cloudflare rotates keys).
func (v *Verifier) key(ctx context.Context, kid string) (*rsa.PublicKey, error) {
	v.mu.Lock()
	defer v.mu.Unlock()
	if k, ok := v.keys[kid]; ok && v.Now().Sub(v.fetched) < keysMaxAge {
		return k, nil
	}
	keys, err := v.fetchKeys(ctx)
	if err != nil {
		if k, ok := v.keys[kid]; ok {
			return k, nil // keep working on the cached key if the refresh fails
		}
		return nil, fmt.Errorf("fetch Access signing keys: %w", err)
	}
	v.keys, v.fetched = keys, v.Now()
	if k, ok := keys[kid]; ok {
		return k, nil
	}
	return nil, fmt.Errorf("%w: unknown key id", ErrInvalidToken)
}

func (v *Verifier) fetchKeys(ctx context.Context) (map[string]*rsa.PublicKey, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, v.CertsURL, nil)
	if err != nil {
		return nil, err
	}
	resp, err := v.Client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("certs endpoint returned %s", resp.Status)
	}
	var doc struct {
		Keys []struct {
			Kid string `json:"kid"`
			Kty string `json:"kty"`
			N   string `json:"n"`
			E   string `json:"e"`
		} `json:"keys"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&doc); err != nil {
		return nil, err
	}
	keys := map[string]*rsa.PublicKey{}
	for _, k := range doc.Keys {
		if k.Kty != "RSA" {
			continue
		}
		n, errN := base64.RawURLEncoding.DecodeString(k.N)
		e, errE := base64.RawURLEncoding.DecodeString(k.E)
		if errN != nil || errE != nil {
			continue
		}
		keys[k.Kid] = &rsa.PublicKey{N: new(big.Int).SetBytes(n), E: int(new(big.Int).SetBytes(e).Int64())}
	}
	if len(keys) == 0 {
		return nil, errors.New("no RSA keys in certs response")
	}
	return keys, nil
}
