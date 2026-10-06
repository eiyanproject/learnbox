package quiz

import (
	"fmt"
	"slices"
)

// Scene is a small diagram of a scenario, seen from above: a road layout and
// the things on it. The browser draws it; nothing here is markup.
//
// The grid is 160 wide and 120 tall with x to the right and y down. "You"
// drive up the page, on the left as in Japan, so on an ordinary road your lane
// is centred on x = 66 and the oncoming lane on x = 94. A heading is in
// degrees clockwise from straight up: 0 up, 90 right, 180 down, 270 left.
//
//	scene:
//	  road: straight
//	  things:
//	    - { is: you, at: [66, 100] }
//	    - { is: bus, at: [62, 48], label: "bus, stopped" }
//	    - { is: car, at: [94, 14], heading: 180 }
type Scene struct {
	Road       string  `yaml:"road" json:"road"`
	Narrow     bool    `yaml:"narrow" json:"narrow,omitempty"`           // straight: a road with no centre line
	NoSidewalk bool    `yaml:"no_sidewalk" json:"no_sidewalk,omitempty"` // straight: no pavement beside it
	Night      bool    `yaml:"night" json:"night,omitempty"`
	Rain       bool    `yaml:"rain" json:"rain,omitempty"`
	Things     []Thing `yaml:"things" json:"things"`
}

// Thing is one item in a scene.
type Thing struct {
	Is      string      `yaml:"is" json:"is"`
	At      []float64   `yaml:"at" json:"at,omitempty"`
	Heading float64     `yaml:"heading" json:"heading,omitempty"`
	Label   string      `yaml:"label" json:"label,omitempty"`
	LabelAt string      `yaml:"label_at" json:"label_at,omitempty"` // right (default), left, above, below
	Blink   string      `yaml:"blink" json:"blink,omitempty"`       // left or right: the indicator that is on
	Lights  bool        `yaml:"lights" json:"lights,omitempty"`     // headlights showing
	Color   string      `yaml:"color" json:"color,omitempty"`       // light: green, yellow or red
	Via     [][]float64 `yaml:"via" json:"via,omitempty"`           // arrow: the points it passes through
}

// The grid a scene is drawn on.
const (
	SceneW = 160
	SceneH = 120
)

var (
	sceneRoads = []string{"straight", "cross", "rail", "merge", "expressway", "bend"}
	// What a scene may hold. "arrow" is the path a driver means to take;
	// "label" is a word on its own.
	sceneThings = []string{
		"you", "car", "van", "bus", "truck", "ambulance", "moped", "bicycle",
		"person", "child", "elder", "ball",
		"crosswalk", "busstop", "light", "arrow", "label",
	}
	labelSides = []string{"", "right", "left", "above", "below"}
)

func (s *Scene) check() error {
	if !slices.Contains(sceneRoads, s.Road) {
		return fmt.Errorf("scene: unknown road %q", s.Road)
	}
	if len(s.Things) == 0 || len(s.Things) > 24 {
		return fmt.Errorf("scene: needs between 1 and 24 things")
	}
	you := 0
	for i, t := range s.Things {
		where := fmt.Sprintf("scene thing %d (%s)", i+1, t.Is)
		if !slices.Contains(sceneThings, t.Is) {
			return fmt.Errorf("scene thing %d: unknown kind %q", i+1, t.Is)
		}
		if t.Is == "you" {
			you++
		}
		if t.Is == "arrow" {
			if len(t.Via) < 2 || len(t.Via) > 4 {
				return fmt.Errorf("%s: via needs 2 to 4 points", where)
			}
			for _, p := range t.Via {
				if !onGrid(p) {
					return fmt.Errorf("%s: via point %v is off the %dx%d grid", where, p, SceneW, SceneH)
				}
			}
		} else {
			if !onGrid(t.At) {
				return fmt.Errorf("%s: at must be [x, y] on the %dx%d grid", where, SceneW, SceneH)
			}
			if len(t.Via) > 0 {
				return fmt.Errorf("%s: only an arrow has via", where)
			}
		}
		if t.Heading < 0 || t.Heading >= 360 {
			return fmt.Errorf("%s: heading is 0 to 359 degrees", where)
		}
		if len([]rune(t.Label)) > 28 {
			return fmt.Errorf("%s: label is longer than 28 characters", where)
		}
		if t.Is == "label" && t.Label == "" {
			return fmt.Errorf("%s: needs a label", where)
		}
		if !slices.Contains(labelSides, t.LabelAt) {
			return fmt.Errorf("%s: label_at is right, left, above or below", where)
		}
		if !slices.Contains([]string{"", "left", "right"}, t.Blink) {
			return fmt.Errorf("%s: blink is left or right", where)
		}
		switch {
		case t.Is == "light" && !slices.Contains([]string{"green", "yellow", "red"}, t.Color):
			return fmt.Errorf("%s: color is green, yellow or red", where)
		case t.Is != "light" && t.Color != "":
			return fmt.Errorf("%s: only a light has a color", where)
		}
	}
	if you != 1 {
		return fmt.Errorf("scene: needs exactly one thing that is you, has %d", you)
	}
	return nil
}

// onGrid allows a little overhang, so a car can be half out of the picture.
func onGrid(p []float64) bool {
	const over = 12
	return len(p) == 2 && p[0] >= -over && p[0] <= SceneW+over && p[1] >= -over && p[1] <= SceneH+over
}
