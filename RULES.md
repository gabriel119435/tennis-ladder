# tennis ladder: rules

a ladder is a continuous ranking format: no elimination, no bracket.
every round, each active player is paired against 2 players close to their current position.
points from every match accumulate over time.
players climb or fall based on results, forever, there is no final.

## roles

only admins log in.
every ranking, every round, every match, every result and every standing is public, visible without a session.
new admin accounts are created only manually, out of band.
the default admin starts with a sample ranking, its reset button wipes and seeds it again.

| who    | can do                                                                                                |
|--------|-------------------------------------------------------------------------------------------------------|
| admin  | creates and renames players, creates rankings, manages participants and rounds, enters/clears results |
| public | (no account) views every ranking, round, match, result and standing                                   |

a player is not an account: an admin creates one as a name only, no password.
a player exists only as something matches and registrations point to.
a player's name must be unique for the admin who created it.
different admins can each have their own player of the same name.

## ownership

players and rankings belong to the admin who created them.
an admin can only register a player into a ranking when they own both.
only the owning admin can rename a player, start/close a ranking, edit its participants or enter/clear its results.
anyone can still view any ranking's standings, rounds and players.
players, matches and rankings are never hard deleted, except by the default admin's reset.
names of players, rankings and admins are stored lowercase, up to 20 characters, no word longer than 15.

## ranking

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
any match still without a result when the round closes becomes a no-match automatically.

## pairing algorithm (runs once, at start)

players are processed in the following fashion: 1st, last, 2nd, 2nd last, ..., converging toward the middle.
for each one still needing opponents:
1. window: up to 5 nearest neighbors above, up to 5 below, each side capped independently.
   if nobody in it has a free slot, it widens by 5 per side until someone does.
2. tiering: group the window by times already played against this player.
   tier 0 = never played, tier 1 = played once, tier 2 = played twice, and so on.
3. selection: walk tiers from 0 up, accumulating until the total reaches 2.
4. prefer whoever played this player longest ago (by round number), random only among remaining ties.
5. the selected candidates become this player's opponents.

if nobody at all has a free slot left, the closest pair is broken and both of its players are paired with this one.
at the end, any 2 players paired twice in the round swap partners with the closest pair not involving them.
every player ends with exactly 2 different opponents, pairing is always mutual.

## match

- a result is entered once and never edited, only cleared and re-entered.
- entering or clearing a result only works while its round is the ranking's open current round.
- a result is either the sets of a played match or the winner of a wo, never both and never neither.
- best of 3 sets: 2-0, or 1-1 decided by set 3: a regular set or a super tiebreak of 10 points.
- 6-6 set is decided by a regular tiebreak: first to 7, win by 2. recorded as 7-6.

**set 1, set 2 and a regular set 3** (games): only valid final scores are 6-0, 6-1, 6-2, 6-3, 6-4, 7-5, or 7-6.

**super tiebreak** (set 3 only, when sets split 1-1): recorded directly as its final score, not as games.
first to 10, win by 2.
loser at 8 or fewer: winner must have exactly 10.
loser at 9 or more: winner must lead by exactly 2 (11-9, 12-10, ...).
any other combination is invalid.
a set 3 score is told apart by its winner: 7 or fewer is a regular set, 10 or more a super tiebreak.

any invalid score is rejected outright, nothing is autocorrected or partially saved.

## walkover (wo)

admin records a wo result with a chosen winner directly, no sets entered.

## no-match

a scheduled pairing that never gets a result: round closes while it's still empty.

## points

| outcome              | points |
|----------------------|--------|
| win (played match)   | +4     |
| loss (played match)  | +1     |
| wo, winner           | +4     |
| wo, the no-show      | -2     |
| no-match, both sides | 0      |

points accumulate forever, never reset.
a fresh ranking is how everyone gets back to 0.

## standings

computed on read: sum of points across all matches, restricted to currently active participants.

attendance: a played match or a wo win counts as attended, a wo as the no-show or a no-match counts as missed.
shown as attended out of matches with a result: 10/12.

leaderboard sorting algo:

1. points (desc).
2. matches missed (asc).
3. matches played (desc), walkovers and no-matches don't count.
4. sets won (desc), set 3 counts as one set, regular or super tiebreak: +1 for whoever wins it.
5. games won (desc), a 7-6 breaker counts as 1 game, already reflected in that 7-6 score.
   a regular set 3 counts its games, a super tiebreak counts as 1 game.
   example: 7-6, 2-6, 10-4 -> player a has won 2 sets, 7+2+1 games.
   example: 6-4, 3-6, 7-5 -> player a has won 2 sets, 6+3+7 games.
6. order of insertion (first registered player is placed on top).
