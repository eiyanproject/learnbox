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

Keep these in mind too, from the owner's standing preferences: ask before
settling a genuine judgement call; do only what was asked; the owner runs
deploys themselves (`bash update-lxc.sh --ctid 116 --yes`, then
`learnbox verify` in the CT).

## Plan: four milestones, each mergeable to main on its own

The first attempt tried to build everything in one pass and stalled. Split
into pieces that each work and ship by themselves:

1. **Profiles** - DONE on this branch (see below). Can be merged now.
2. **XP, levels and badges** - the scoring engine (a pure package, computed
   from a progress snapshot, unit-tested), a profile summary endpoint, rewards
   returned with each check, an XP/level indicator in the top bar, a badges
   page, toasts. No timed challenges yet.
3. **Arena, one track** - challenge start/forfeit endpoints, the server-side
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

## Done on this branch

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
