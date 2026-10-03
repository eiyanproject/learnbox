package content

import "strings"

// Example is one checkable code block from a lesson body.
type Example struct {
	// Line is the lesson.md line of the block's first line of code, so a
	// failure can point at the exact place in the file.
	Line   int    `json:"line"`
	Source string `json:"source"`
}

// Program is a complete program from a lesson body together with the output
// the lesson says it prints.
type Program struct {
	Line   int    `json:"line"`
	Source string `json:"source"`
	Output string `json:"output"`
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
	for _, f := range l.fences() {
		if f.tag == lang && f.source != "" {
			out = append(out, Example{Line: l.BodyLine + f.first, Source: f.source})
		}
	}
	return out
}

// Programs returns every block tagged lang that is followed directly - with
// nothing but blank lines between - by an ```output block.
//
// The output block is the opt-in, as the transcript tag is for Examples: it
// says "this is a whole program, and this is what it prints". It is also what
// the learner sees under the code, so a lesson gains the output and a check
// of it in one edit.
func (l *Lesson) Programs(lang string) []Program {
	var out []Program
	fs := l.fences()
	for i := 0; i+1 < len(fs); i++ {
		code, shown := fs[i], fs[i+1]
		if code.tag != lang || shown.tag != "output" || code.source == "" || !shown.follows(code) {
			continue
		}
		out = append(out, Program{
			Line:   l.BodyLine + code.first,
			Source: code.source,
			Output: shown.source,
		})
		i++ // the output block is used up
	}
	return out
}

// fence is one closed fenced code block, positioned by body line index.
type fence struct {
	tag          string
	open, close  int // the fence lines themselves
	first        int // first line of code, open+1
	source       string
	blankBetween bool // only blank lines since the previous fence closed
}

func (f fence) follows(prev fence) bool { return f.blankBetween && f.open > prev.close }

func (l *Lesson) fences() []fence {
	var out []fence
	lines := strings.Split(l.Body, "\n")
	inFence := false
	indent := ""
	var cur fence
	var code []string
	blank := false // every line since the last closing fence was blank
	for i, raw := range lines {
		// A lesson edited on Windows may carry CRLF; neither the compilers nor
		// the output comparison should see the CR.
		line := strings.TrimRight(raw, "\r")
		trimmed := strings.TrimLeft(line, " \t")
		if !strings.HasPrefix(trimmed, "```") {
			if inFence {
				code = append(code, strings.TrimPrefix(line, indent))
			} else if strings.TrimSpace(line) != "" {
				blank = false
			}
			continue
		}
		if !inFence {
			inFence = true
			indent = line[:len(line)-len(trimmed)]
			cur = fence{
				tag:          strings.TrimSpace(strings.TrimPrefix(trimmed, "```")),
				open:         i,
				first:        i + 1,
				blankBetween: blank && len(out) > 0,
			}
			code = nil
			continue
		}
		// A closing fence ends whatever block is open.
		cur.close = i
		if len(code) > 0 {
			cur.source = strings.Join(code, "\n") + "\n"
		}
		out = append(out, cur)
		inFence, blank = false, true
	}
	return out
}
