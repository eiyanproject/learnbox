package content

import "testing"

func TestExamplesCollectsOnlyTheTaggedLanguage(t *testing.T) {
	l := &Lesson{BodyLine: 10, Body: "intro\n" +
		"```python\nnot_run()\n```\n" + // illustrative: ignored
		"text\n" +
		"```pycon\n>>> 1 + 1\n2\n```\n" + // a transcript: collected
		"```pycon\n>>> x = 3\n>>> x * 2\n6\n```\n"}
	ex := l.Examples("pycon")
	if len(ex) != 2 {
		t.Fatalf("got %d examples, want 2: %+v", len(ex), ex)
	}
	if ex[0].Source != ">>> 1 + 1\n2\n" {
		t.Errorf("first example = %q", ex[0].Source)
	}
	if ex[1].Source != ">>> x = 3\n>>> x * 2\n6\n" {
		t.Errorf("second example = %q", ex[1].Source)
	}
}

func TestExamplesReportTheLineInLessonMD(t *testing.T) {
	// Body line 0 is file line 10. The pycon fence is body line 2, so its first
	// code line is body line 3 - file line 13.
	l := &Lesson{BodyLine: 10, Body: "a\nb\n```pycon\n>>> 1\n1\n```\n"}
	ex := l.Examples("pycon")
	if len(ex) != 1 || ex[0].Line != 13 {
		t.Fatalf("got %+v, want one example at line 13", ex)
	}
}

func TestExamplesHandleIndentedFences(t *testing.T) {
	// A fence inside a list item is indented; the indent is not part of the code.
	l := &Lesson{Body: "- item\n\n  ```pycon\n  >>> 2 + 2\n  4\n  ```\n"}
	ex := l.Examples("pycon")
	if len(ex) != 1 || ex[0].Source != ">>> 2 + 2\n4\n" {
		t.Fatalf("got %+v", ex)
	}
}

func TestExamplesIgnoreAnUnterminatedFence(t *testing.T) {
	l := &Lesson{Body: "```pycon\n>>> 1\n1\n"}
	if ex := l.Examples("pycon"); len(ex) != 0 {
		t.Fatalf("an unterminated block should not be collected: %+v", ex)
	}
}

func TestExamplesNoneWhenAbsent(t *testing.T) {
	l := &Lesson{Body: "```rust\nfn main() {}\n```\n"}
	if ex := l.Examples("pycon"); len(ex) != 0 {
		t.Fatalf("got %+v", ex)
	}
}
