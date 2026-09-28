import random

import pytest

from app.pairing import (
    _find_any_duplicate,
    _find_pool,
    _repair_excluded_player,
    _repair_duplicate,
    _order_in_two_fronts,
    build_round_pairings,
    get_pairing_window,
    select_opponents,
)


@pytest.mark.parametrize(
    "standings_order, player_id, window_size, expected",
    [
        # interior, one side short
        (list(range(20, 30)), 26, 10, [21, 22, 23, 24, 25, 27, 28, 29]),
        # n small enough that both sides are short
        ([1, 2, 3, 4, 5], 3, 10, [1, 2, 4, 5]),
        # top of the standings, nothing above
        (list(range(20, 30)), 20, 10, [21, 22, 23, 24, 25]),
    ],
)
def test_get_pairing_window(standings_order, player_id, window_size, expected):
    assert get_pairing_window(standings_order, player_id, window_size) == expected


@pytest.mark.parametrize(
    "pool, times_played, needed, must_include",
    [
        # tier 0 candidate always makes the cut
        ([3, 4, 5, 6], {4: 1, 5: 1, 6: 1}, 2, [3]),
        # all tier 0, any single one is valid
        ([3, 4, 5, 6], {}, 1, []),
        ([3, 4], {3: 2, 4: 0}, 1, [4]),
    ],
)
def test_select_opponents_prefers_lower_tier(pool, times_played, needed, must_include):
    result = select_opponents(pool, times_played, needed, random.Random(0))
    assert len(result) == needed
    assert len(set(result)) == needed  # no duplicates
    for candidate in must_include:
        assert candidate in result


def test_select_opponents_prefers_least_recently_played_within_a_tier():
    # 3 and 4 tie on times_played (both 1); 3 was played longer ago (round 2 vs round 9).
    # 3 must win regardless of the shuffle, correct for every seed, not just one.
    pool = [3, 4]
    times_played = {3: 1, 4: 1}
    last_played = {3: 2, 4: 9}
    for seed in range(20):
        assert select_opponents(pool, times_played, 1, random.Random(seed), last_played) == [3]


def test_select_opponents_falls_back_to_random_within_a_true_tie():
    # 3 and 4 tie on both times_played and last_played: which one wins must vary across seeds.
    pool = [3, 4]
    times_played = {3: 1, 4: 1}
    last_played = {3: 5, 4: 5}
    results = {
        select_opponents(pool, times_played, 1, random.Random(seed), last_played)[0] for seed in range(20)
    }
    assert results == {3, 4}


@pytest.mark.parametrize(
    "standings_order, expected",
    [
        ([1, 2, 3], [1, 3, 2]),
        ([1, 2, 3, 4], [1, 4, 2, 3]),
        (list(range(1, 11)), [1, 10, 2, 9, 3, 8, 4, 7, 5, 6]),
    ],
)
def test_order_in_two_fronts(standings_order, expected):
    assert _order_in_two_fronts(standings_order) == expected


def test_find_pool_widens_until_a_candidate_is_found():
    standings = list(range(1, 31))
    remaining = {30: 1}  # everyone else already 0, 30 is far outside the initial window
    assert _find_pool(standings, 15, remaining) == [30]


def test_find_pool_returns_empty_when_nobody_has_a_slot():
    standings = [1, 2, 3, 4, 5]
    assert _find_pool(standings, 3, {}) == []


def test_find_pool_reaches_the_opposite_edge_from_an_edge_player():
    standings = list(range(1, 102))
    remaining = {101: 1}
    assert _find_pool(standings, 1, remaining) == [101]


def test_repair_excluded_player_breaks_the_closest_pair():
    pairs = [(10, 20), (6, 16)]
    pos = {x: x for x in range(1, 30)}
    _repair_excluded_player(pairs, pos, 11)
    assert pairs == [(10, 20), (11, 6), (11, 16)]


@pytest.mark.parametrize(
    "pairs, expected",
    [
        ([(1, 2), (3, 4)], None),
        ([(1, 2), (3, 4), (3, 4)], (3, 4)),
        ([(1, 2), (10, 20), (20, 10)], (20, 10)),  # order-flipped duplicate still found
    ],
)
def test_find_any_duplicate(pairs, expected):
    assert _find_any_duplicate(pairs) == expected


def test_repair_duplicate_keeps_one_copy_and_reconnects_the_rest():
    pairs = [(1, 2), (10, 20), (10, 20)]
    pos = {x: x for x in range(1, 21)}
    _repair_duplicate(pairs, pos, 10, 20)
    assert pairs == [(10, 20), (10, 1), (20, 2)]


def test_build_round_pairings_rejects_too_few_participants():
    with pytest.raises(ValueError, match="too_few_active_participants"):
        build_round_pairings([1, 2], {}, random.Random(0))


def test_build_round_pairings_3_players_forces_the_full_triangle():
    pairs = build_round_pairings([1, 2, 3], {}, random.Random(0))
    assert (
            {frozenset(pair) for pair in pairs} ==
            {frozenset((1, 2)), frozenset((1, 3)), frozenset((2, 3))}
    )


@pytest.mark.parametrize("n", [3, 4, 5, 10, 20, 30, 40, 50, 100, 200, 300])
def test_build_round_pairings_always_gives_exactly_2_distinct_opponents(n):
    standings = list(range(1, n + 1))
    for seed in range(20):
        pairs = build_round_pairings(standings, {}, random.Random(seed))
        opponents = {player_id: [] for player_id in standings}
        for a, b in pairs:
            assert a != b
            opponents[a].append(b)
            opponents[b].append(a)
        for player_id, opps in opponents.items():
            assert len(opps) == 2, (n, seed, player_id, opps)
            assert len(set(opps)) == 2, (n, seed, player_id, opps)


def test_build_round_pairings_cannot_avoid_all_repeats():
    """
    3 veterans have already played each other. 2 newcomers haven't played anyone.

    veterans need 6 opponent-slots total (3*2). newcomers can cover at most 4 (2*2).
    the other 2 slots can only go to another veteran: at least 1 repeat is forced, for any seed.

    with 5 players, the only way to give everyone 2 distinct opponents is one single 5-cycle.
    where the 2 newcomers land in that cycle decides whether 1 or 2 of those slots become repeats.

    newcomers apart: 77-80-78-81-79-77. only (79, 77) closes the cycle between two veterans. 1 repeat.
    newcomers together: 77-78-79-80-81-77. veterans bunch into one run, (77, 78) and (78, 79) repeat. 2 repeats.

    both are valid rounds, the construction has no preference between them.
    so the only thing always true, for any seed, is at least 1 repeat, never exactly 1.
    """
    standings = [77, 78, 79, 80, 81]
    history = {77: {78: 1, 79: 1}, 78: {77: 1, 79: 1}, 79: {77: 1, 78: 1}}
    pairs = build_round_pairings(standings, history, random.Random(0))
    repeats = sum(1 for a, b in pairs if history.get(a, {}).get(b, 0) > 0)
    assert repeats >= 1
