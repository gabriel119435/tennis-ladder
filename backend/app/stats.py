from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Match, Player, RankingParticipant
from app.scoring import POINTS, games_won, sets_won, standings_sort_key


def compute_history(session, ranking_id):
    """
    tuple of dicts where 1st is count of matches and second is the most recent round
    returns: tuple[dict, dict] player id -> {opponent id -> times played}, player id -> {opponent id -> round}

    example: this ranking has 2 "played" matches: (10, 20) in round 1, (10, 30) in round 3
    returns (
        # times played
        {10: {20: 1, 30: 1}, 20: {10: 1}, 30: {10: 1}},
        # round most recently played
        {10: {20: 1, 30: 3}, 20: {10: 1}, 30: {10: 3}}
    )
    """
    history = {}
    last_played = {}
    played = session.execute(
        select(Match.player_a_id, Match.player_b_id, Match.round).where(
            Match.ranking_id == ranking_id, Match.result_type == "played"
        )
    ).all()
    for a, b, round_ in played:
        history.setdefault(a, {})
        history.setdefault(b, {})
        history[a][b] = history[a].get(b, 0) + 1
        history[b][a] = history[b].get(a, 0) + 1

        last_played.setdefault(a, {})
        last_played.setdefault(b, {})
        last_played[a][b] = max(last_played[a].get(b, 0), round_)
        last_played[b][a] = max(last_played[b].get(a, 0), round_)
    return history, last_played


def compute_standings(session, ranking_id):
    """
    standings for this ranking's active players, sorted by standings_sort_key.
    returns: list[dict] one row per active player, [] when the ranking has none. example:
    rows = [
        {"id": 10, "name": "alice", "points": 4, "won_matches": 1, "lost_matches": 0,
        "attended_matches": 1, "total_matches": 1, "won_sets": 2, "lost_sets": 0, "won_games": 12, "lost_games": 7},

        {"id": 20, "name": "bob", "points": 1, "won_matches": 0, "lost_matches": 1,
         "attended_matches": 1, "total_matches": 1, "won_sets": 0, "lost_sets": 2, "won_games": 7, "lost_games": 12},
    ]
    """
    participant_id_by_player_id, names = _get_active_players_per_ranking(session, ranking_id)
    if not participant_id_by_player_id:
        return []

    matches = session.scalars(
        # selectinload loads every match's sets in one extra query, avoids 1+N
        select(Match).options(selectinload(Match.sets)).where(Match.ranking_id == ranking_id)
    ).all()

    fields = (
        "points",
        "won_matches",
        "lost_matches",
        "attended_matches",
        "total_matches",
        "won_sets",
        "lost_sets",
        "won_games",
        "lost_games",
    )
    stats = {player_id: dict.fromkeys(fields, 0) for player_id in participant_id_by_player_id}
    for match in matches:
        _accumulate(stats, match)

    rows = [{"id": player_id, "name": names[player_id], **stat} for player_id, stat in stats.items()]
    rows.sort(
        key=lambda row: standings_sort_key(
            row["points"],
            row["won_matches"],
            row["lost_matches"],
            row["total_matches"] - row["attended_matches"],
            row["won_sets"],
            row["won_games"],
            participant_id_by_player_id[row["id"]],
        )
    )
    return rows


def _get_active_players_per_ranking(session, ranking_id):
    # returns 2 dicts: player_id: participant_id and player_id: name
    rows = session.execute(
        select(RankingParticipant.player_id, RankingParticipant.id, Player.name)
        .join(Player, Player.id == RankingParticipant.player_id)
        .where(RankingParticipant.ranking_id == ranking_id, RankingParticipant.active.is_(True))
    ).all()
    participant_id_by_player_id = {player_id: participant_id for player_id, participant_id, _ in rows}
    names = {player_id: name for player_id, _, name in rows}
    return participant_id_by_player_id, names


def _accumulate(stats, match):
    """
    returns: None, adds the match to both players' totals in stats, in place
    example: match.player_a_id=10, match.player_b_id=20, match.result_type="played", match.winner_id=10
    match.sets holds [(6, 4), (6, 3)]
    stats before: {10: {"points": 0, "won_matches": 0, ..., "lost_games": 0}, 20: {same, all 0}}
    stats after:  {10: {"points": 4, "won_matches": 1, "lost_matches": 0, "attended_matches": 1, "total_matches": 1,
                        "won_sets": 2, "lost_sets": 0, "won_games": 12, "lost_games": 7},
                   20: {"points": 1, "won_matches": 0, "lost_matches": 1, "attended_matches": 1, "total_matches": 1,
                        "won_sets": 0, "lost_sets": 2, "won_games": 7, "lost_games": 12}}
    """
    # still empty, the match has yet to happen
    if match.result_type is None:
        return
    # sets = [(6, 4), (6, 3)]
    sets = [(set_.games_a, set_.games_b) for set_ in match.sets]
    # for ... in ((10, "a", "b"), (20, "b", "a"))
    for player_id, side, other_side in ((match.player_a_id, "a", "b"), (match.player_b_id, "b", "a")):
        if player_id not in stats:
            continue
        stats[player_id]["total_matches"] += 1
        if match.result_type == "played":
            stats[player_id]["attended_matches"] += 1
            won = match.winner_id == player_id
            stats[player_id]["won_matches" if won else "lost_matches"] += 1

            # what the other side won is what this side lost
            stats[player_id]["won_sets"] += sets_won(sets, side)
            stats[player_id]["lost_sets"] += sets_won(sets, other_side)

            stats[player_id]["won_games"] += games_won(sets, side)
            stats[player_id]["lost_games"] += games_won(sets, other_side)

            outcome = "win" if won else "loss"
        elif match.result_type == "walkover":
            won = match.winner_id == player_id
            if won:
                stats[player_id]["attended_matches"] += 1
            outcome = "wo_winner" if won else "wo_loser"
        else:
            outcome = "no_match"
        stats[player_id]["points"] += POINTS[outcome]
