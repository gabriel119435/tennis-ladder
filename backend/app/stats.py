from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Player, Match, RankingParticipant
from app.scoring import games_won, points_for, sets_won, standings_sort_key


def compute_history(session, ranking_id):
    """
    tuple of dicts where 1st is count of matches and second is the most recent round

    example: this ranking has 2 "played" matches: (10, 20) in round 1, (10, 30) in round 3
    returns (
        {10: {20: 1, 30: 1}, 20: {10: 1}, 30: {10: 1}},  # times played
        {10: {20: 1, 30: 3}, 20: {10: 1}, 30: {10: 3}},  # round most recently played
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
    standings for this ranking's active players, sorted by standings_sort_key. example:
    rows = [
        {"id": 10, "name": "alice", "points": 100, "sets": 2, "games": 12, "matches_played": 1},
        {"id": 20, "name": "bob", "points": 25, "sets": 0, "games": 7, "matches_played": 1},
    ]
    """
    participant_id_by_player_id, names = _get_active_players_per_ranking(session, ranking_id)
    if not participant_id_by_player_id:
        return []

    matches = session.scalars(
        select(Match)
        .options(selectinload(Match.sets))  # avoids 1+N
        .where(Match.ranking_id == ranking_id)
    ).all()

    stats = {
        player_id: {"points": 0, "sets": 0, "games": 0, "matches_played": 0}
        for player_id in participant_id_by_player_id
    }
    for match in matches:
        _accumulate(stats, match)

    rows = [{"id": player_id, "name": names[player_id], **stat} for player_id, stat in stats.items()]
    rows.sort(
        key=lambda row: standings_sort_key(
            row["points"], row["sets"], row["games"], row["matches_played"], participant_id_by_player_id[row["id"]]
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
    participant_id_by_player_id = {player_id: participant_id for player_id, participant_id, name in rows}
    names = {player_id: name for player_id, participant_id, name in rows}
    return participant_id_by_player_id, names


def _accumulate(stats, match):
    """
    example: match.player_a_id=10, match.player_b_id=20, match.result_type="played", match.winner_id=10
    match.sets holds [(6, 4), (6, 3)]
    stats before: {10: {"points": 0, "sets": 0, "games": 0, "matches_played": 0}, 20: {same, all 0}}
    stats after:  {10: {"points": 100, "sets": 2, "games": 12, "matches_played": 1},
                   20: {"points": 25, "sets": 0, "games": 7, "matches_played": 1}}
    """
    # sets = [(6, 4), (6, 3)]
    sets = [(set_.games_a, set_.games_b) for set_ in match.sets]
    # for ... in ((10, "a"), (20, "b"))
    for player_id, side in ((match.player_a_id, "a"), (match.player_b_id, "b")):
        if player_id not in stats:
            continue
        stats[player_id]["matches_played"] += 1
        if match.result_type == "played":
            stats[player_id]["sets"] += sets_won(sets, side)
            stats[player_id]["games"] += games_won(sets, side)
            outcome = "win" if match.winner_id == player_id else "loss"
        elif match.result_type == "walkover":
            outcome = "wo_winner" if match.winner_id == player_id else "wo_loser"
        else:
            outcome = "no_match"
        stats[player_id]["points"] += points_for(outcome)
