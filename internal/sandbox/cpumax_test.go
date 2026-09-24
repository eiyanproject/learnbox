package sandbox

import "testing"

func TestParseCPUMax(t *testing.T) {
	cases := []struct {
		in   string
		want string
	}{
		{"150%", "150000 100000"},
		{"100%", "100000 100000"},
		{"50%", "50000 100000"},
		{"200%", "200000 100000"},
		{"max", "max"},
		{"", "max"},
		{"  150%  ", "150000 100000"},
		{"150000 100000", "150000 100000"}, // already in cgroup form
	}
	for _, c := range cases {
		got, err := ParseCPUMax(c.in)
		if err != nil {
			t.Errorf("ParseCPUMax(%q): unexpected error %v", c.in, err)
			continue
		}
		if got != c.want {
			t.Errorf("ParseCPUMax(%q) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestParseCPUMaxRejectsNonsense(t *testing.T) {
	// A typo here must not quietly become "uncapped": the service exits instead.
	for _, in := range []string{"1.5", "150", "abc", "0%", "-50%", "%"} {
		if got, err := ParseCPUMax(in); err == nil {
			t.Errorf("ParseCPUMax(%q) = %q, want an error", in, got)
		}
	}
}
