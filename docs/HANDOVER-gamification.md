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

## Done on this branch

- `internal/profiles` - the profile registry (`profiles.json` in the data
  dir). The first start creates profile `default`, which keeps the existing
  `progress.json` and `~/learn`, so nothing moves. Other profiles get
  `progress-<id>.json` and `~/profiles/<id>/learn`. Ids are validated
  (`ValidID`) because they become paths. Create, rename, delete (not the last
  one; lesson files are left on disk). Tested.
- `internal/workspace` - `Manager.For(base)` returns a view whose lesson
  folders live under `base`; `Rel` and the reset backups follow it.
- `internal/progress` - `Challenge` records (server-side start and deadline,
  wins, losses, cooldown, best time and XP) and earned-badge timestamps, with
  `Snapshot`, `Challenge`, `UpdateChallenge`, `AwardBadges`.
- `internal/content` - a track section may be `arena: true`; its lessons
  carry a `challenge:` front-matter block (`boss`, `minutes`,
  `cooldown_minutes`, `xp`, `requires: {xp, badges}`), with defaults applied
  and validation (a challenge needs tests and must sit in an arena section).
  `Neighbours` keeps arena lessons and ordinary lessons apart.

`GOOS=linux go vet ./...` is clean and the package tests pass.

## Still to do

1. **The scoring engine** - XP per lesson, levels with titles, the badge
   catalogue (global and per track), challenge unlock rules (every earlier
   round won, plus `requires`), win rewards with a speed bonus, settling an
   expired attempt into a loss and cooldown. Computed from the progress
   snapshot, so earlier passes count automatically. Unit-test it.
2. **Server wiring** - pick the profile per request from a cookie (validate
   with `profiles.ValidID`; if only one profile exists, use it; otherwise ask
   the frontend to show a picker); use the profile's progress store and
   `Workspace.For(profiles.WorkspaceBase(id))` everywhere a lesson is read,
   written, reset or checked (call `Runner.CheckDir` with the profile's
   workspace); key terminal sessions by profile too. Endpoints for profiles
   (list, create, select, rename, delete), the profile summary (XP, level,
   badges), the arena, and challenge start and forfeit. A check on a
   challenge only counts inside a running attempt that has not expired.
   Return the rewards (XP gained, level change, new badges) with every check.
3. **Frontend** - profile picker and switcher, an XP and level indicator in
   the top bar, a badges page, an Arena page with each track's ladder and its
   locks, and the challenge view in the lesson page (start, countdown,
   forfeit, win and loss, cooldown). Toasts for XP, level-ups and badges.
4. **Content** - an `arena` section in every `track.yaml` and a ladder in each
   track: a few timed rounds of rising difficulty, then a boss. Each needs
   starter, solution and tests, and must pass `learnbox verify`. Set the
   unlock thresholds per track from the XP that track can actually award.
5. **Docs** - README: profiles, the game rules, how to write a challenge.
6. Then **suggest what could come next**, as the owner asked.

The verify harness from the previous work (lesson examples) is unaffected.
To test a track end to end, the scripts used before ran `learnbox verify`
inside each toolchain's Docker image (see the README section on writing
lessons for what verify checks).
