import pytest

from app.scoring import (
    POINTS,
    games_won,
    match_winner,
    sets_won,
    standings_sort_key,
    valid_set_score,
    valid_super_tiebreak_score,
)


@pytest.mark.parametrize(
    "games_a, games_b, expected",
    [
        (6, 0, True),
        (6, 1, True),
        (6, 2, True),
        (6, 3, True),
        (6, 4, True),
        (7, 5, True),
        (7, 6, True),
        # reversed order still valid
        (0, 6, True),
        (6, 7, True),
        # must continue to 7-5, not stop at 6-5
        (6, 5, False),
        # no such regular set score
        (8, 6, False),
        (7, 4, False),
        # not finished, needs a breaker
        (6, 6, False),
        (0, 0, False),
        (7, 7, False),
        (-1, 6, False),
    ],
)
def test_valid_set_score(games_a, games_b, expected):
    assert valid_set_score(games_a, games_b) is expected


@pytest.mark.parametrize(
    "points_a, points_b, expected",
    [
        (10, 0, True),
        (10, 5, True),
        (10, 8, True),
        (11, 9, True),
        (12, 10, True),
        (20, 18, True),
        # order doesn't matter
        (0, 10, True),
        (8, 10, True),
        # loser at 9+ needs a 2-point lead, not 1
        (10, 9, False),
        (9, 10, False),
        (10, 10, False),
        # loser <= 8 means winner must be exactly 10
        (11, 8, False),
        (-1, 10, False),
        (10, -1, False),
        # winner capped at MAX_TIEBREAK_POINTS
        (30, 28, True),
        (31, 29, False),
    ],
)
def test_valid_super_tiebreak_score(points_a, points_b, expected):
    assert valid_super_tiebreak_score(points_a, points_b) is expected


@pytest.mark.parametrize(
    "sets, expected_winner",
    [
        ([(6, 4), (6, 3)], "a"),
        ([(4, 6), (3, 6)], "b"),
        # split sets, super tiebreak decides
        ([(6, 4), (4, 6), (10, 7)], "a"),
        ([(6, 4), (4, 6), (7, 10)], "b"),
        # split sets, a regular 3rd set decides
        ([(6, 4), (4, 6), (7, 5)], "a"),
        ([(6, 4), (4, 6), (3, 6)], "b"),
    ],
)
def test_match_winner_valid(sets, expected_winner):
    assert match_winner(sets) == expected_winner


@pytest.mark.parametrize(
    "sets, error",
    [
        ([(6, 4)], "invalid_set_count"),
        ([(6, 4), (6, 3), (6, 2), (6, 1)], "invalid_set_count"),
        ([(8, 6), (6, 3)], "invalid_set_score"),
        # 2-0 already, no 3rd set allowed
        ([(6, 4), (6, 3), (6, 2)], "invalid_set_count"),
        # split sets, no 3rd set
        ([(6, 4), (4, 6)], "invalid_set_count"),
        # neither a regular set nor a super tiebreak
        ([(6, 4), (4, 6), (10, 9)], "invalid_set_score"),
        ([(6, 4), (4, 6), (8, 6)], "invalid_set_score"),
    ],
)
def test_match_winner_invalid(sets, error):
    with pytest.raises(ValueError, match=error):
        match_winner(sets)


@pytest.mark.parametrize(
    "sets, side, expected_sets_won, expected_games_won",
    [
        ([(6, 4), (6, 3)], "a", 2, 12),
        ([(6, 4), (6, 3)], "b", 0, 7),
        ([(7, 6), (2, 6), (12, 10)], "a", 2, 10),
        ([(7, 6), (2, 6), (12, 10)], "b", 1, 12),
        # a regular 3rd set counts its games, 6 + 3 + 7 and 4 + 6 + 5
        ([(6, 4), (3, 6), (7, 5)], "a", 2, 16),
        ([(6, 4), (3, 6), (7, 5)], "b", 1, 15),
    ],
)
def test_sets_and_games_won(sets, side, expected_sets_won, expected_games_won):
    assert sets_won(sets, side) == expected_sets_won
    assert games_won(sets, side) == expected_games_won


@pytest.mark.parametrize(
    "outcome, expected",
    [
        ("win", 4),
        ("loss", 1),
        ("wo_winner", 4),
        ("wo_loser", -2),
        ("no_match", 0),
    ],
)
def test_points(outcome, expected):
    assert POINTS[outcome] == expected


@pytest.mark.parametrize(
    "row_a, row_b",
    [
        # input: points, missed_matches, played_matches, won_sets, won_games, participant_id
        # order: -points, missed_matches, -played_matches, -won_sets, -won_games, participant_id
        ((1, 0, 0, 0, 0, "higher_points"), (0, 0, 0, 0, 0, "lower_points")),
        ((0, 0, 0, 0, 0, "fewer_missed"), (0, 1, 0, 0, 0, "more_missed")),
        ((0, 0, 1, 0, 0, "more_played"), (0, 0, 0, 0, 0, "fewer_played")),
        ((0, 0, 0, 1, 0, "more_sets"), (0, 0, 0, 0, 0, "fewer_sets")),
        ((0, 0, 0, 0, 1, "more_games"), (0, 0, 0, 0, 0, "fewer_games")),
        ((0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 1)),
    ],
)
def test_standings_sort_key(row_a, row_b):
    ordered = sorted([row_b, row_a], key=lambda row: standings_sort_key(*row))
    assert ordered == [row_a, row_b]
