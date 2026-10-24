VALID_SET_SCORES = {(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (7, 5), (7, 6)}

POINTS = {
    "win": 4,
    "loss": 1,
    "wo_winner": 4,
    "wo_loser": -2,
    "no_match": 0,
}


def valid_set_score(games_a, games_b):
    return (games_a, games_b) in VALID_SET_SCORES or (games_b, games_a) in VALID_SET_SCORES


def valid_super_tiebreak_score(points_a, points_b):
    if points_a < 0 or points_b < 0:
        return False
    winner, loser = max(points_a, points_b), min(points_a, points_b)
    if loser <= 8:
        return winner == 10
    return winner - loser == 2


def valid_third_set_score(games_a, games_b):
    return valid_set_score(games_a, games_b) or valid_super_tiebreak_score(games_a, games_b)


def _set_winner(set_score):
    games_a, games_b = set_score
    return "a" if games_a > games_b else "b"


def match_winner(sets):
    if len(sets) not in (2, 3):
        raise ValueError("invalid_set_count")

    set1, set2 = sets[0], sets[1]
    if not valid_set_score(*set1) or not valid_set_score(*set2):
        raise ValueError("invalid_set_score")

    winner1, winner2 = _set_winner(set1), _set_winner(set2)

    # 2-0 takes exactly 2 sets, a 1-1 split takes a 3rd one
    if (winner1 == winner2) != (len(sets) == 2):
        raise ValueError("invalid_set_count")
    if len(sets) == 2:
        return winner1

    if not valid_third_set_score(*sets[2]):
        raise ValueError("invalid_set_score")
    return _set_winner(sets[2])


def sets_won(sets, side):
    return sum(1 for _set in sets if _set_winner(_set) == side)


def games_won(sets, side):
    total = 0
    for games_a, games_b in sets:
        if valid_set_score(games_a, games_b):
            total += games_a if side == "a" else games_b
        else:
            total += 1 if _set_winner((games_a, games_b)) == side else 0
    return total


def standings_sort_key(
    points,
    won_matches,
    lost_matches,
    missed_matches,
    won_sets,
    won_games,
    participant_id,
):
    return (
        -points,
        missed_matches,
        -(won_matches + lost_matches),
        -won_sets,
        -won_games,
        participant_id,
    )
