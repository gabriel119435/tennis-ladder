VALID_SET_SCORES = {(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (7, 5), (7, 6)}

POINTS = {
    "win": 100,
    "loss": 25,
    "wo_winner": 100,
    "wo_loser": -100,
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

    if winner1 == winner2:
        if len(sets) != 2:
            raise ValueError("unexpected_third_set")
        return winner1

    if len(sets) != 3:
        raise ValueError("missing_super_tiebreak")
    if not valid_super_tiebreak_score(*sets[2]):
        raise ValueError("invalid_super_tiebreak_score")
    return _set_winner(sets[2])


def sets_won(sets, side):
    """
    count of sets side won; a super tiebreak (a 3rd entry) counts as one set, same as a regular set.

    sets: list[tuple[int, int]]: (games_a, games_b) per set, in the order played.
    side: str: 'a' or 'b'.
    returns: int: sets won by side.

    example: sets=[(7, 6), (2, 6), (12, 10)], side='a'
    _set_winner((7, 6))   == 'a'  (7 > 6)    -> counted
    _set_winner((2, 6))   == 'b'  (2 < 6)    -> not counted
    _set_winner((12, 10)) == 'a'  (12 > 10)  -> counted
    sum = 2
    """
    return sum(1 for set_score in sets if _set_winner(set_score) == side)


def games_won(sets, side):
    """
    games side won: a regular set's games (index 0 or 1) count directly.
    a super tiebreak (index 2, if present) counts as 1 game.

    sets: list[tuple[int, int]]: (games_a, games_b) per set, in the order played.
    side: str: 'a' or 'b'.
    returns: int: games won by side.

    example: sets=[(7, 6), (2, 6), (12, 10)], side='a'
    i=0, (7, 6),   i < 2  -> total += games_a = 7    -> total = 7
    i=1, (2, 6),   i < 2  -> total += games_a = 2    -> total = 9
    i=2, (12, 10), i >= 2 -> _set_winner(...) == 'a' -> total += 1 -> total = 10
    returns 10
    """
    total = 0
    for i, (games_a, games_b) in enumerate(sets):
        if i < 2:
            total += games_a if side == "a" else games_b
        else:
            total += 1 if _set_winner((games_a, games_b)) == side else 0
    return total


def points_for(outcome):
    return POINTS[outcome]


def standings_sort_key(points, sets, games, matches_played, participant_id):
    return -points, -sets, -games, -matches_played, participant_id
