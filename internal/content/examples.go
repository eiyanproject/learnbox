package content

import "strings"

// Example is one checkable code block from a lesson body.
type Example struct {
	// Line is the lesson.md line of the block's first line of code, so a
	// failure can point at the exact place in the file.
	Line   int    `json:"line"`
	Source string `json:"source"`
}

// Examples returns the lesson's fenced code blocks tagged with lang, in the
// order they appear.
//
// Only an exact tag matches: ```pycon is collected for "pycon", while
// ```python is not. That is the opt-in. Most blocks in a lesson are fragments
// - half a statement, a deliberately vulnerable snippet, a name defined three
// paragraphs earlier - and running them would bury real errors under false
// ones. A transcript tag is the author saying "this one states its result;
// check it".
func (l *Lesson) Examples(lang string) []Example {
	var out []Example
	lines := strings.Split(l.Body, "\n")
	inFence, collecting := false, false
	indent := ""
	var cur []string
	start := 0
	for i, line := range lines {
		trimmed := strings.TrimLeft(line, " \t")
		if !strings.HasPrefix(trimmed, "```") {
			if collecting {
				cur = append(cur, strings.TrimPrefix(line, indent))
			}
			continue
		}
		if !inFence {
			inFence = true
			indent = line[:len(line)-len(trimmed)]
			tag := strings.TrimSpace(strings.TrimPrefix(trimmed, "```"))
			collecting = tag == lang
			cur, start = nil, i+1
			continue
		}
		// A closing fence ends whatever block is open.
		if collecting && len(cur) > 0 {
			out = append(out, Example{
				Line:   l.BodyLine + start,
				Source: strings.Join(cur, "\n") + "\n",
			})
		}
		inFence, collecting = false, false
	}
	return out
}
