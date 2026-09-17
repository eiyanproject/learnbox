// Package exercism converts an Exercism language track checkout
// (github.com/exercism/<lang>, MIT licensed) into learnbox lessons:
//
//	stub files        -> starter/
//	test files        -> tests/     (hidden, added at check time)
//	.meta/example.*   -> solution/  (for `learnbox verify` only)
//	.docs/*.md        -> lesson.md body, hints.md -> hints
package exercism

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"

	"gopkg.in/yaml.v3"
)

type trackConfig struct {
	Exercises struct {
		Practice []struct {
			Slug       string `json:"slug"`
			Name       string `json:"name"`
			Difficulty int    `json:"difficulty"`
			Status     string `json:"status"`
		} `json:"practice"`
	} `json:"exercises"`
}

type exerciseConfig struct {
	Files struct {
		Solution []string `json:"solution"`
		Test     []string `json:"test"`
		Example  []string `json:"example"`
	} `json:"files"`
	Blurb string `json:"blurb"`
}

type Report struct {
	Imported int
	Skipped  map[string]string // slug -> reason
}

// Import writes <out>/<lang>/practice/<slug>/ for every usable exercise.
// It builds into a sibling directory and swaps it in, so a failed import
// leaves the previous one intact.
func Import(lang, src, out string) (*Report, error) {
	raw, err := os.ReadFile(filepath.Join(src, "config.json"))
	if err != nil {
		return nil, err
	}
	var tc trackConfig
	if err := json.Unmarshal(raw, &tc); err != nil {
		return nil, fmt.Errorf("track config.json: %w", err)
	}

	final := filepath.Join(out, lang, "practice")
	staging := final + ".new"
	if err := os.RemoveAll(staging); err != nil {
		return nil, err
	}
	if err := os.MkdirAll(staging, 0o755); err != nil {
		return nil, err
	}

	rep := &Report{Skipped: map[string]string{}}
	for _, ex := range tc.Exercises.Practice {
		if ex.Status == "deprecated" {
			rep.Skipped[ex.Slug] = "deprecated"
			continue
		}
		reason, err := importOne(lang, filepath.Join(src, "exercises", "practice", ex.Slug), filepath.Join(staging, ex.Slug), ex.Slug, ex.Name, ex.Difficulty)
		if err != nil {
			return nil, fmt.Errorf("%s: %w", ex.Slug, err)
		}
		if reason != "" {
			rep.Skipped[ex.Slug] = reason
			os.RemoveAll(filepath.Join(staging, ex.Slug))
			continue
		}
		rep.Imported++
	}

	old := final + ".old"
	os.RemoveAll(old)
	if _, err := os.Stat(final); err == nil {
		if err := os.Rename(final, old); err != nil {
			return nil, err
		}
	}
	if err := os.Rename(staging, final); err != nil {
		return nil, err
	}
	os.RemoveAll(old)
	return rep, nil
}

var (
	rustDeps     = regexp.MustCompile(`(?ms)^\[(dev-)?dependencies\]\s*\n(.*?)(^\[|\z)`)
	headingMark  = regexp.MustCompile(`(?m)^#`)
	hintSplit    = regexp.MustCompile(`(?m)^## `)
	outOfLineMod = regexp.MustCompile(`(?m)^\s*(pub\s+)?mod\s+\w+\s*;`)
)

func importOne(lang, dir, dst, slug, name string, difficulty int) (skip string, err error) {
	raw, err := os.ReadFile(filepath.Join(dir, ".meta", "config.json"))
	if err != nil {
		return "no .meta/config.json", nil
	}
	var cfg exerciseConfig
	if err := json.Unmarshal(raw, &cfg); err != nil {
		return "bad .meta/config.json", nil
	}
	if len(cfg.Files.Solution) == 0 || len(cfg.Files.Test) == 0 {
		return "no solution or test files listed", nil
	}

	var editable []string
	switch lang {
	case "python":
		editable = cfg.Files.Solution
	case "rust":
		cargo, err := os.ReadFile(filepath.Join(dir, "Cargo.toml"))
		if err != nil {
			return "no Cargo.toml", nil
		}
		for _, m := range rustDeps.FindAllStringSubmatch(string(cargo), -1) {
			for _, line := range strings.Split(m[2], "\n") {
				line = strings.TrimSpace(line)
				if line != "" && !strings.HasPrefix(line, "#") {
					return "needs crates from crates.io", nil
				}
			}
		}
		for _, f := range cfg.Files.Solution {
			if strings.HasSuffix(f, ".rs") {
				editable = append(editable, f)
			}
		}
	default:
		return "", fmt.Errorf("unsupported language %q", lang)
	}

	// starter: the stub files, plus anything else the exercise ships outside
	// .docs/.meta/tests (Cargo.toml, .gitignore, data files).
	testSet := map[string]bool{}
	for _, t := range cfg.Files.Test {
		testSet[filepath.ToSlash(t)] = true
	}
	err = filepath.WalkDir(dir, func(p string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		rel, _ := filepath.Rel(dir, p)
		rel = filepath.ToSlash(rel)
		if d.IsDir() {
			if rel == ".docs" || rel == ".meta" || rel == "tests" || rel == "target" {
				return filepath.SkipDir
			}
			return nil
		}
		if testSet[rel] {
			// Python tests sit next to the stub; Rust tests live in tests/.
			target := filepath.Base(rel)
			return copyFile(p, filepath.Join(dst, "tests", target))
		}
		return copyFile(p, filepath.Join(dst, "starter", filepath.FromSlash(rel)))
	})
	if err != nil {
		return "", err
	}
	if lang == "rust" {
		for _, t := range cfg.Files.Test {
			if err := copyFile(filepath.Join(dir, t), filepath.Join(dst, "tests", filepath.Base(t))); err != nil {
				return "", err
			}
		}
	}

	// solution: the starter with the example written over the stub. Only
	// possible when there is exactly one example file and one stub to replace.
	if lang == "rust" && len(cfg.Files.Example) == 1 {
		if ex, err := os.ReadFile(filepath.Join(dir, cfg.Files.Example[0])); err == nil && outOfLineMod.Match(ex) {
			return "solution needs module files the exercise does not ship", nil
		}
	}
	if len(cfg.Files.Example) == 1 && len(editable) == 1 {
		if err := copyFile(filepath.Join(dir, cfg.Files.Example[0]), filepath.Join(dst, "solution", filepath.FromSlash(editable[0]))); err != nil {
			return "", err
		}
	}

	body := readDocs(dir)
	hints := readHints(filepath.Join(dir, ".docs", "hints.md"))
	run := ""
	switch lang {
	case "python":
		run = "python -i " + editable[0]
	case "rust":
		run = "cargo build"
	}
	front := map[string]any{
		"title":      name,
		"summary":    cfg.Blurb,
		"difficulty": difficulty,
		"files":      editable,
		"run":        run,
		"source": fmt.Sprintf("From the [Exercism %s track](https://github.com/exercism/%s/tree/main/exercises/practice/%s), MIT License.",
			titleCase(lang), lang, slug),
	}
	if len(hints) > 0 {
		front["hints"] = hints
	}
	fm, err := yaml.Marshal(front)
	if err != nil {
		return "", err
	}
	lesson := "---\n" + string(fm) + "---\n" + body
	return "", os.WriteFile(filepath.Join(dst, "lesson.md"), []byte(lesson), 0o644)
}

func readDocs(dir string) string {
	var parts []string
	for _, name := range []string{"introduction.md", "instructions.md", "instructions.append.md"} {
		raw, err := os.ReadFile(filepath.Join(dir, ".docs", name))
		if err != nil {
			continue
		}
		text := strings.TrimSpace(strings.ReplaceAll(string(raw), "\r\n", "\n"))
		// Each file starts with its own "# Title"; demote so the lesson title
		// stays the only h1.
		text = headingMark.ReplaceAllString(text, "##")
		parts = append(parts, text)
	}
	return strings.Join(parts, "\n\n") + "\n"
}

// readHints turns hints.md into one hint per "## " section. Exercism
// hints.md files open with a "## General" section, which comes first.
func readHints(path string) []string {
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil
	}
	text := strings.ReplaceAll(string(raw), "\r\n", "\n")
	var hints []string
	for _, chunk := range hintSplit.Split(text, -1)[1:] {
		chunk = strings.TrimSpace(chunk)
		if chunk == "" {
			continue
		}
		title, rest, _ := strings.Cut(chunk, "\n")
		hints = append(hints, "**"+strings.TrimSpace(title)+"**\n\n"+strings.TrimSpace(rest))
	}
	sort.SliceStable(hints, func(a, b int) bool {
		return strings.HasPrefix(hints[a], "**General") && !strings.HasPrefix(hints[b], "**General")
	})
	return hints
}

func copyFile(src, dst string) error {
	raw, err := os.ReadFile(src)
	if err != nil {
		return err
	}
	if err := os.MkdirAll(filepath.Dir(dst), 0o755); err != nil {
		return err
	}
	return os.WriteFile(dst, raw, 0o644)
}

func titleCase(s string) string {
	if s == "" {
		return s
	}
	return strings.ToUpper(s[:1]) + s[1:]
}
