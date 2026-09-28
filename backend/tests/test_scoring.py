import pytest

from app.scoring import (
    games_won,
    match_winner,
    points_for,
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
        (0, 6, True),  # reversed order still valid
        (6, 7, True),
        (6, 5, False),  # must continue to 7-5, not stop at 6-5
        (8, 6, False),  # no such regular set score
        (7, 4, False),
        (6, 6, False),  # not finished, needs a breaker
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
        (0, 10, True),  # order doesn't matter
        (8, 10, True),
        (10, 9, False),  # loser at 9+ needs a 2-point lead, not 1
        (9, 10, False),
        (10, 10, False),
        (11, 8, False),  # loser <= 8 means winner must be exactly 10
        (-1, 10, False),
        (10, -1, False),
    ],
)
def test_valid_super_tiebreak_score(points_a, points_b, expected):
    assert valid_super_tiebreak_score(points_a, points_b) is expected


@pytest.mark.parametrize(
    "sets, expected_winner",
    [
        ([(6, 4), (6, 3)], "a"),
        ([(4, 6), (3, 6)], "b"),
        ([(6, 4), (4, 6), (10, 7)], "a"),  # split sets, super tiebreak decides
        ([(6, 4), (4, 6), (7, 10)], "b"),
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
        ([(6, 4), (6, 3), (6, 2)], "unexpected_third_set"),  # 2-0 already, no 3rd set allowed
        ([(6, 4), (4, 6)], "missing_super_tiebreak"),  # split sets, no decider
        ([(6, 4), (4, 6), (10, 9)], "invalid_super_tiebreak_score"),
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
    ],
)
def test_sets_and_games_won(sets, side, expected_sets_won, expected_games_won):
    assert sets_won(sets, side) == expected_sets_won
    assert games_won(sets, side) == expected_games_won


@pytest.mark.parametrize(
    "outcome, expected",
    [
        ("win", 100),
        ("loss", 25),
        ("wo_winner", 100),
        ("wo_loser", -100),
        ("no_match", 0),
    ],
)
def test_points_for(outcome, expected):
    assert points_for(outcome) == expected


@pytest.mark.parametrize(
    "row_a, row_b",
    [
        ((200, 1, 1, 1, "higher_points"), (100, 1, 1, 1, "lower_points")),
        ((100, 5, 1, 1, "more_sets"), (100, 3, 1, 1, "fewer_sets")),
        ((100, 5, 20, 1, "more_games"), (100, 5, 10, 1, "fewer_games")),
        ((100, 5, 10, 5, "more_matches"), (100, 5, 10, 2, "fewer_matches")),
        ((100, 5, 10, 3, 1), (100, 5, 10, 3, 2)),
    ],
)
def test_standings_sort_key(row_a, row_b):
    ordered = sorted([row_b, row_a], key=lambda row: standings_sort_key(*row))
    assert ordered == [row_a, row_b]
