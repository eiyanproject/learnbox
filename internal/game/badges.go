package game

import (
	"time"

	"github.com/eiyanproject/learnbox/internal/content"
)

// Badge families, in the order the badges page shows them.
const (
	Milestone  = "milestone"
	Completion = "completion"
	Style      = "style"
	Calendar   = "calendar"
	ArenaFam   = "arena"
	Secret     = "secret"
)

// Badge is one badge as a learner sees it.
type Badge struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Family      string    `json:"family"`
	Earned      bool      `json:"earned"`
	EarnedAt    time.Time `json:"earned_at,omitzero"`
	// Have of Want is how far along an unearned badge is.
	Have int `json:"have"`
	Want int `json:"want"`
}

type def struct {
	id, name, desc, family string
	// progress reports how far along the badge is; it is met at have >= want.
	progress func(*stats) (have, want int)
}

// badge renders a definition for one learner. A secret badge gives nothing
// away - not its name, not how close it is - until it is earned.
func (d def) badge(st *stats, earned bool, at time.Time) Badge {
	b := Badge{ID: d.id, Name: d.name, Description: d.desc, Family: d.family, Earned: earned}
	if earned {
		b.EarnedAt = at
		return b
	}
	if d.family == Secret {
		b.Name, b.Description = "???", "A secret. Keep going."
		return b
	}
	b.Have, b.Want = d.progress(st)
	b.Have = min(b.Have, b.Want)
	return b
}

func count(n func(*stats) int, want int) func(*stats) (int, int) {
	return func(st *stats) (int, int) { return n(st), want }
}

func flag(f func(*stats) bool) func(*stats) (int, int) {
	return func(st *stats) (int, int) {
		if f(st) {
			return 1, 1
		}
		return 0, 1
	}
}

var (
	passed   = func(st *stats) int { return st.passed }
	level    = func(st *stats) int { return st.level }
	sections = func(st *stats) int { return st.sectionsDone }
	beginner = func(st *stats) int { return st.beginnerDone }
	touched  = func(st *stats) int { return st.tracksTouched }
	practice = func(st *stats) int { return st.practicePassed }
	firstTry = func(st *stats) int { return st.firstTry }
	streak   = func(st *stats) int { return st.streak }
)

var fixed = []def{
	{"first-pass", "Hello, World!", "Pass your first lesson.", Milestone, count(passed, 1)},
	{"lessons-10", "Double Digits", "Pass 10 lessons.", Milestone, count(passed, 10)},
	{"lessons-50", "Half a Hundred", "Pass 50 lessons.", Milestone, count(passed, 50)},
	{"lessons-100", "Centurion", "Pass 100 lessons.", Milestone, count(passed, 100)},
	{"lessons-250", "Is There Anything Left?", "Pass 250 lessons.", Milestone, count(passed, 250)},
	{"level-5", "Getting the Hang of It", "Reach level 5.", Milestone, count(level, 5)},
	{"level-10", "Ten Out of Ten", "Reach level 10.", Milestone, count(level, 10)},
	{"level-20", "Senior-ish", "Reach level 20.", Milestone, count(level, 20)},
	{"level-30", "Final Form", "Reach level 30.", Milestone, count(level, 30)},

	{"beginner-1", "Not a Beginner Anymore!", "Finish a track's Beginner section.", Completion, count(beginner, 1)},
	{"beginner-3", "Serial Beginner", "Finish the Beginner section of 3 tracks.", Completion, count(beginner, 3)},
	{"sections-5", "Chapter Collector", "Finish 5 sections.", Completion, count(sections, 5)},
	{"sections-20", "Shelf Filler", "Finish 20 sections.", Completion, count(sections, 20)},
	{"tracks-3", "Dabbler", "Pass a lesson in 3 different tracks.", Completion, count(touched, 3)},
	{"tracks-5", "Jack of All Trades", "Pass a lesson in 5 different tracks.", Completion, count(touched, 5)},
	{"tracks-all", "Everything Everywhere", "Pass a lesson in every track.", Completion,
		func(st *stats) (int, int) { return st.tracksTouched, max(st.tracksTotal, 1) }},
	{"practice-10", "Practice Makes Permanent", "Pass 10 practice exercises.", Completion, count(practice, 10)},
	{"practice-50", "Gym Rat", "Pass 50 practice exercises.", Completion, count(practice, 50)},

	{"no-hints", "Look Ma, No Hints!", "Finish a section without revealing a single hint.", Style,
		count(func(st *stats) int { return st.noHintSections }, 1)},
	{"first-try-5", "Nailed It", "Pass 5 lessons on the first attempt.", Style, count(firstTry, 5)},
	{"first-try-25", "One-Take Wonder", "Pass 25 lessons on the first attempt.", Style, count(firstTry, 25)},
	{"persistent", "Tenth Time's the Charm", "Pass a lesson that took you 10 attempts or more.", Style,
		count(func(st *stats) int { return st.maxAttempts }, 10)},
	{"all-hints", "Asked for Directions", "Pass a lesson after reading every hint it has.", Style,
		flag(func(st *stats) bool { return st.allHints })},

	{"streak-3", "Three's a Habit", "Pass a lesson 3 days in a row.", Calendar, count(streak, 3)},
	{"streak-7", "A Whole Week", "Pass a lesson 7 days in a row.", Calendar, count(streak, 7)},
	{"streak-30", "Monthly Subscription", "Pass a lesson 30 days in a row.", Calendar, count(streak, 30)},
	{"day-5", "On a Roll", "Pass 5 lessons in one day.", Calendar,
		count(func(st *stats) int { return st.bestDay }, 5)},
	{"night-owl", "Night Owl", "Pass a lesson between midnight and 5 in the morning.", Calendar,
		flag(func(st *stats) bool { return st.nightOwl })},
	{"early-bird", "Early Bird", "Pass a lesson between 5 and 7 in the morning.", Calendar,
		flag(func(st *stats) bool { return st.earlyBird })},
	{"weekend", "Weekend Warrior", "Pass a lesson on both days of one weekend.", Calendar,
		flag(func(st *stats) bool { return st.weekend })},

	{"arena-first", "Into the Arena", "Win an arena challenge.", ArenaFam,
		count(func(st *stats) int { return st.arenaWins }, 1)},
	{"arena-10", "Gladiator", "Win 10 different arena challenges.", ArenaFam,
		count(func(st *stats) int { return st.arenaWins }, 10)},
	{"boss-1", "Boss Slayer", "Beat a boss.", ArenaFam,
		count(func(st *stats) int { return st.bossWins }, 1)},
	{"boss-3", "Boss Rush", "Beat the boss of 3 tracks.", ArenaFam,
		count(func(st *stats) int { return st.bossWins }, 3)},
	{"boss-all", "No Bosses Left", "Beat every boss there is.", ArenaFam,
		func(st *stats) (int, int) { return st.bossWins, max(st.bossTotal, 1) }},
	{"arena-fast", "Blink and You'll Miss It", "Win a challenge in under a quarter of its time.", ArenaFam,
		flag(func(st *stats) bool { return st.fastWin })},
	{"boss-flawless", "One Shot, One Boss", "Beat a boss at the first attempt.", ArenaFam,
		flag(func(st *stats) bool { return st.flawlessBoss })},
	{"arena-comeback", "Came Back Swinging", "Win a challenge you had lost 3 times.", ArenaFam,
		flag(func(st *stats) bool { return st.comeback })},

	{"lucky-13", "Lucky Thirteen", "Pass a lesson on exactly the thirteenth attempt.", Secret,
		flag(func(st *stats) bool { return st.lucky13 })},
	{"speedrun", "Did You Even Read It?", "Pass a lesson within two minutes of first opening it.", Secret,
		flag(func(st *stats) bool { return st.speedrun })},
	{"new-year", "New Year's Resolution", "Pass a lesson on the first of January.", Secret,
		flag(func(st *stats) bool { return st.newYear })},
}

// defs is every badge there is: the fixed ones, then one per track for
// finishing its guided lessons, placed after the other completion badges.
func defs(lib *content.Library) []def {
	var out []def
	for i, d := range fixed {
		out = append(out, d)
		if d.family == Completion && fixed[i+1].family != Completion {
			out = append(out, trackDefs(lib)...)
		}
	}
	return out
}

func trackDefs(lib *content.Library) []def {
	var out []def
	for _, t := range lib.Tracks {
		guided := 0
		for _, sec := range t.Sections {
			if sec.Arena {
				continue
			}
			for _, l := range sec.Lessons {
				if l.HasTest && l.Difficulty == 0 {
					guided++
				}
			}
		}
		if guided == 0 {
			continue
		}
		name := t.Badge
		if name == "" {
			name = "Finished " + t.Title
		}
		lang := t.Lang
		out = append(out, def{
			id: "track-" + lang, name: name, family: Completion,
			desc: "Pass every guided lesson in " + t.Title + ".",
			progress: func(st *stats) (int, int) {
				ts := st.byLang[lang]
				return ts.guidedPassed, ts.guided
			},
		})
	}
	return out
}
