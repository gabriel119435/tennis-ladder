# tennis ladder: rules

a ladder is a continuous ranking format: no elimination, no bracket.
every round, each active player is paired against 2 players close to their current position.
points from every match accumulate over time.
players climb or fall based on results, forever, there is no final.

## roles

only admins log in.
every ranking, every round, every match, every result and every standing is public, visible without a session.
new admin accounts are created only manually, out of band.

| who    | can do                                                                                                   |
|--------|----------------------------------------------------------------------------------------------------------|
| admin  | logs in; creates and renames players, creates rankings, manages participants and rounds, upserts results |
| public | (no account) views every ranking, round, match, result and standing                                      |

a player is not an account: an admin creates one as a name only, no password.
a player exists only as something matches and registrations point to.
a player's name must be unique for the admin who created it.
different admins can each have their own player of the same name.

## ownership

players and rankings belong to the admin who created them.
an admin can only register a player into a ranking when they own both.
an admin can only rename a player, or start/close a ranking or edit its participants/results if they own it.
anyone can still view any ranking's standings, rounds and players.
players, matches and rankings are never hard deleted.

## ranking

a ranking's name is free text.
the name must be unique for the admin who created it.
a round is open for scoring only while the ranking is ongoing, it starts idle.
the round number goes up by 1 every time a round starts.
going idle again just means paused, not finished, it can always resume with a new round.

## registration

a player can be registered to any number of rankings.
a player can join a ranking at any time, even mid-ranking, always starting with 0 points.
removing a player from a ranking marks them inactive, it never deletes any match or score.
an inactive player keeps every point already earned, but is excluded from future pairing.
an inactive player can rejoin at any time, with nothing recalculated.
standings only list currently active players.

## starting and closing a round

starting a round requires at least 3 active participants.
starting flips the ranking to ongoing, moves to the next round, and generates that round's matches.
this check is identical for a ranking's very first round or any later resume, nothing else is checked.
closing has no checks at all, it just flips the ranking back to idle.
any match still without a result when the round closes become a no-match automatically.

## pairing algorithm (runs once, at start)

for every active participant, in the ranking's current standings order:
1. window: up to 5 nearest neighbors above, up to 5 below, each side capped independently.
2. tiering: group the window by times already played against this player.
   tier 0 = never played, tier 1 = played once, tier 2 = played twice, and so on.
3. selection: walk tiers from 0 up, accumulating until the total reaches 2.
4. prefer whoever played this player longest ago (by round number), random only among remaining ties.
5. the 2 selected candidates become this player's opponents.

pairing must stay mutual: if A's selection includes B, B's selection must include A.

## match

- results can only be upserted while their round is the ranking's open current round.
- best of 3 sets: 2-0, or 1-1 decided by a super tiebreak of 10 points.
- 6-6 set is decided by a regular tiebreak: first to 7, win by 2. recorded as 7-6.

**set 1 and set 2** (games): only valid final scores are 6-0, 6-1, 6-2, 6-3, 6-4, 7-5, or 7-6.

**super tiebreak** (only if sets split 1-1): recorded directly as its final score, not as games.
first to 10, win by 2.
loser at 8 or fewer: winner must have exactly 10.
loser at 9 or more: winner must lead by exactly 2 (11-9, 12-10, ...).
any other combination is invalid.

any invalid score is rejected outright, nothing is autocorrected or partially saved.

## walkover (wo)

admin records a wo result with a chosen winner directly, no sets entered.

## no-match

a scheduled pairing that never gets a result: round closes while it's still empty.

## points

| outcome              | points |
|----------------------|--------|
| win (played match)   | +100   |
| loss (played match)  | +25    |
| wo, winner           | +100   |
| wo, the no-show      | -100   |
| no-match, both sides | 0      |

points accumulate forever, never reset.
a fresh ranking is how everyone gets back to 0.

## standings

computed on read: sum of points across all matches, restricted to currently active participants.

leaderboard sorting algo:

1. points (desc)
2. sets won (desc) — a super tiebreak counts as one set: +1 for whoever wins it
3. games won (desc) — a 7-6 breaker counts as 1 game, already reflected in that 7-6 score.
   a super tiebreak also counts as 1 game.
   example: 7-6, 2-6, 10-4 -> player a has won 2 sets, 7+2+1 games.
4. matches played (desc)
5. order of insertion (first registered player is placed on top)
