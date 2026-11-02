# pending/future tasks

## pending

## future

- scoped css: move each single-owner rule into its vue file's `<style scoped>` with mobile `@media` part included.
    - shared rules stay global in the itcss layers: tokens, reset, elements, shared layout, shared mobile rules.
    - also covers `table.css:25`/`:36` duplicate selector, `.mobile-only`, `.toggle-button`, `name-form.css` cascade.
    - update FRONT_READ.md.
- permanent delete: an admin deletes own rankings and players, each independently.
- player filter: a player picker below the matches tab's ranking picker, shows one player's matches only.
    - options in standings order, plus a clear entry via `clear-label`, like the wo picker (`MatchCard.vue:115`).
    - no localStorage, unlike the ranking picker's `useRememberedPick`, a reload starts with no player picked.
    - standings list active players only, so a player removed mid-round can't be picked.
- player history: a new tab, ranking picker, player picker below it, then the player's rounds, newest first.
    - each round: a `round N - start position X` header, then the player's matches of that round.
    - match rows reuse the public matches display (`MatchCard`, read only).
    - start position per round needs new backend logic, only current standings are computed today.
    - player options from `/api/rankings/<id>/participants`, active players only, a removed player can't be picked.
- rules summary: points and tie-break order below the standings table, text from one pt-br i18n key.
    - points per result: win 4, loss 1, wo win 4, wo loss -2, no-match 0 (`scoring.py:5`).
    - tie-break order in one line: points, fewest missed, most played, sets won, games won, registration.
    - `RULES.md` and `scoring.py` stay the source, the i18n text changes with them.
- public read cache: nginx keeps rankings, standings and matches for a few seconds, if standings load the pi.
    - logged-in requests skip it, so an owner never sees a stale result right after saving.
- cache `load_user`: it runs a `session.get` on every authenticated request, worth it if traffic grows.
- two click confirm: port grade-tracker's `ConfirmButton.vue` + `useConfirm.js` to reset and close.
    - 1st click shows a confirmation state for 3s, 2nd click runs it, remove player stays one click (reversible).
    - also needs the `.btn-danger-confirm` css and a `common.confirmation` pt-br key.
- stale tab writes issue: a tab left open across another admin's login writes as the new admin.
    - creates land under the new admin, edits to the old admin's rankings fail with 403 `not_owner`.
- player accounts: players become separate unique accounts, used in any admin's rankings at the same time.
    - a validated email, unique, identifies the player and validates the account.
    - only someone with access to that email can rename the player or register themselves.
    - a password change or reset must invalidate other sessions, like grade-tracker's `AuthUser.get_id()`.
    - merging v1's duplicated players happens in 2 steps.
    - step 1: add a validated email column, not unique yet.
    - step 2: merge player rows that share the same email.
