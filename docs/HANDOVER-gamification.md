# Handover: profiles and gamification (work in progress)

Branch `gamification`. Not merged, not deployed. `main` is untouched.

## What the owner asked for

1. **Gamification.** Experience points for passing lessons, levels, and badges
   (achievements) with light-hearted names - "Not a Beginner Anymore!" was the
   owner's own example. A **challenge mode**: timed programming challenges
   with gradual progression - a few rounds, then a **boss fight**. A challenge
   unlocks with a certain badge and/or amount of XP.
2. **Profiles.** Simple user creation and selection, **no login** - the owner
   uses the box alone for now and may add real logins later if friends join.

## Decisions the owner made (do not re-ask)

| Question | Answer |
|---|---|
| Which tracks get challenge mode | **Every track** (python, rust, c, cpp, java, csharp, matlab, ccna, mindset, security) |
| When the timer runs out | **The attempt is lost, then a short cooldown** before retrying |
| Lessons passed before this ships | **Count them** for XP and badges |
| Hints | **Each hint revealed costs a little XP**, with a floor |

Scoring decisions, made 2026-10-05:

| Question | Answer |
|---|---|
| Lesson XP | **Scaled by section**: an `xp:` per section in `track.yaml` (50 / 75 / 100 / 150) |
| Practice exercises | **10 XP x Exercism difficulty** (10-100) |
| Hint cost | **10% of the lesson each, floor 50%**; hints read after the pass are free |
| Badge families | **All four offered**: milestones and completion, style, calendar, secret |

Keep these in mind too, from the owner's standing preferences: ask before
settling a genuine judgement call; do only what was asked; the owner runs
deploys themselves (`bash update-lxc.sh --ctid 116 --yes`, then
`learnbox verify` in the CT).

## Plan: four milestones, each mergeable to main on its own

The first attempt tried to build everything in one pass and stalled. Split
into pieces that each work and ship by themselves:

1. **Profiles** - DONE, merged to main and deployed (c6d5661).
2. **XP, levels and badges** - DONE on this branch. The scoring engine (a pure package, computed
   from a progress snapshot, unit-tested), a profile summary endpoint, rewards
   returned with each check, an XP/level indicator in the top bar, a badges
   page, toasts. No timed challenges yet.
3. **Arena, one track** - DONE on this branch. Challenge start/forfeit endpoints, the server-side
   clock, loss and cooldown, unlock rules, the Arena page and the countdown in
   the lesson view, with the Python ladder (rounds then a boss) as content.
4. **Arena, every other track** - ladders for rust, c, cpp, java, csharp,
   matlab, ccna, mindset and security, each passing `learnbox verify`. The
   owner chose every track; this order only decides what ships first.

Then README docs for the game rules and how to write a challenge, and
**suggestions for what could come next**, as the owner asked.

A note for whoever continues: two responses in the original session were
stopped by a safety filter, the second while writing the scoring engine.
That session carried a great deal of security-course material (attack
walkthroughs); a session without it is the better place for this work. Keep
any security-track challenges defensive (detect, decode, fix, harden).

## After gamification: a Japanese driving test practice track

The owner asked (2026-10-05) for a Japanese driving licence written-test
practice, in a **Misc** area kept separate from the programming tracks. They
said to do gamification **first**; this comes after. Decisions already made
(do not re-ask):

| Question | Answer |
|---|---|
| Which test | **Both**, the provisional licence test (仮免) first, then the full licence test (本免) |
| Language | **English with the Japanese underneath**, so the real test's terms are learned |
| Practice modes | **All three**: study by topic (each answer explained with its rule), timed mock exam at the real pass mark, and a mistakes review that drills previously wrong questions |

Exam formats (checked 2026-10-05):

- 仮免 written test: 50 true/false questions, 30 minutes, 2 points each, pass
  at 90 of 100 (at most 5 wrong).
- 本免 written test: 90 true/false questions (1 point each) and 5 illustration
  questions (2 points each, every illustration has 3 statements and scores
  only if all 3 are right), 50 minutes, pass at 90 of 100.

Sources: [Fine Motor School on the 仮免 test](https://www.fine-motorschool.co.jp/news/column/20240226/),
[Kanagawa Prefectural Police licence procedure](https://www.police.pref.kanagawa.jp/tetsuzuki/menkyo/mes83012.html),
[日本合宿免許予約センター on the 本免 test](https://www.gasshukuhikaku.com/blog_car/post_6378/).

How it was going to be built - a starting point, not a decision:

- **Questions are original**, written from the National Police Agency's
  交通の方法に関する教則 (a National Public Safety Commission notice; Japanese
  copyright law excludes official notices, Art. 13). Commercial question
  banks and driving-school books are copyrighted: do not copy them. Each
  question records which rule it rests on, and every numeric fact (distances,
  speeds, times) is checked against the official text - a wrong "fact" here
  is worse than none.
- This is a **new lesson type**: true/false and illustration questions, not
  code plus tests, so it needs a quiz format (questions with answers, English
  and Japanese text, explanations, which exam each can appear in), validated
  when content loads, and its own pages: topic study, timed mock exam,
  mistakes review. Per-profile records of answers and exam results.
- A track-level flag to show it under **Misc** instead of with the
  programming tracks, on the home page and in the rail.
- Illustration questions need pictures; plain SVG scene diagrams, or text
  scenarios to start with, are the options.
- Once XP exists, quiz topics and passed mock exams can award it.

## Done on this branch

- **Milestone 3.** `internal/game/arena.go`: the rules as pure functions
  (unlocking, start, win with speed bonus, loss and cooldown) with tests.
  `internal/httpapi/arena.go`: `GET /api/arena`, `POST
  .../challenge/start` and `.../challenge/forfeit`, and Check for an arena
  lesson. An expired attempt is settled as a loss by whoever looks next;
  nothing runs on a timer. A challenge's text, files and shell answer 409
  `challenge_not_started` outside an attempt until it has been won. Frontend:
  `/arena`, the countdown and Forfeit in the lesson view. Content: the Python
  ladder (`content/python/arena`, three rounds and a boss), passing `learnbox
  verify python/arena`. Eight arena badges. `learnbox_challenges_total`.
  Calls made without asking: speed bonus up to +50%, linear in time left;
  replaying a won challenge is allowed and keeps the best result; every
  attempt starts from the starter files; arena lessons have no hints and are
  left out of the track pages and lesson counts.

- **Milestone 2.** `internal/game`: XP, hint cost, levels and badges as pure
  functions of the library and a progress snapshot, with tests. `GET
  /api/summary`; `reward` in every check response; `xp`, `xp_full` and
  `hint_cost` on a lesson. The progress entry gained `pass_attempts` and
  `free_hints`, recorded from now on (older passes fall back to the totals).
  Frontend: level chip in the top bar, `/badges`, reward cards after a check,
  the hint button shows its cost. `LEARNBOX_TZ` sets whose day it is.
  Calls made without asking: the level curve (level n at 50n(n-1) XP), rank
  titles every five levels, the badge names and thresholds, and that
  "guided" (for track badges) means a lesson with no difficulty rating.

- `internal/profiles` - the profile registry (`profiles.json` in the data
  dir). The first start creates profile `default` ("Learner"), which keeps the
  existing `progress.json` and `~/learn`, so nothing moves. Other profiles get
  `progress-<id>.json` and `~/profiles/<id>/learn`. Ids are validated
  (`ValidID`) because they become paths. Create, rename, delete (not the last;
  lesson files are kept). Tested.
- **Server** - each request acts for the profile its `learnbox_profile`
  cookie names, or the only one; with several and none picked the API returns
  409 `{"code":"choose_profile"}`. Lessons, files, checks (via
  `Runner.CheckDir` on the profile's workspace), hints, resets and terminals
  all use the profile's store and folder; terminals for non-default profiles
  are keyed `profile/<id>/...`, and clients may not ask for that prefix.
  Endpoints: `GET/POST /api/profiles`, `POST /api/profiles/{id}/select`,
  `POST /api/profiles/{id}/rename`, `DELETE /api/profiles/{id}`. Tested
  (`internal/httpapi/profiles_test.go`).
- **Frontend** - a profile button in the top bar opening a picker (pick,
  create, rename, delete); the picker opens by itself when the server asks.
  Picking reloads the page to drop the old profile's state.
- **Verified in a browser** against a real server: creating a profile
  switches to it, a lesson passed as one profile does not touch another's
  progress or files, terminals are separate per profile.
- Groundwork for milestones 2-4, not yet used: challenge records and
  earned-badge timestamps in `internal/progress`; arena sections and the
  `challenge:` front matter in `internal/content` (validated: a challenge
  needs tests and must sit in an arena section; `Neighbours` keeps arena and
  ordinary lessons apart).
- README describes profiles and what they are not (not a login).

All Go tests pass (`go test ./...` in a golang:1.26 container) and the
frontend builds.

The verify harness from the previous work (lesson examples) is unaffected.
To test a track end to end, the scripts used before ran `learnbox verify`
inside each toolchain's Docker image (see the README section on writing
lessons for what verify checks).
