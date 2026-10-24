MIN_ACTIVE_TO_START = 3
INITIAL_WINDOW_SIZE = 10


def get_pairing_window(standings_order, player_id, window_size=INITIAL_WINDOW_SIZE):
    """
    returns up to window_size/2 neighbors above player_id and up to window_size/2 below.

    standings_order: list[int]: player ids, strongest ranked first.
    player_id: int: the player to build a window around.
    window_size: int: max neighbors to return, split evenly across both sides.
    returns: list[int]: the neighbors found, above followed by below.

    example: standings_order=[20, ..., 29], window_size=10, player_id=22. so pos=2 and half=5
    above = standings_order[0:2] = [20, 21]              (only 2 exist, short side stays short)
    below = standings_order[3:8] = [23, 24, 25, 26, 27]  (5 available)
    returns [20, 21, 23, 24, 25, 26, 27]
    """
    pos = standings_order.index(player_id)
    half = window_size // 2
    above = standings_order[max(0, pos - half) : pos]
    below = standings_order[pos + 1 : pos + 1 + half]
    return above + below


def select_opponents(pool, times_played, needed, rng, last_played=None):
    """
    select up to `needed` opponents from pool, preferring whoever has played this player least.
    within a tier, prefer whoever played this player longest ago, remaining ties broken randomly.

    pool: list[int]: candidate player ids.
    times_played: dict[int, int]: candidate id -> times already played this player, 0 if absent.
    needed: int: how many opponents to pick (1 or 2).
    rng: random.Random: source of randomness, shuffled once per tier.
    last_played: dict[int, int] | None: candidate id -> round they most recently played this player, 0 if absent.
    returns: list[int]: the `needed` chosen ids. may be fewer.

    example: pool=[3, 4, 5, 10], times_played={3: 1, 4: 1, 5: 1}
    needed=2, tiers = {0: [10], 1: [3, 4, 5]}

    tier 0: candidates=[10], chosen.extend(candidates[:2]) -> chosen = [10], still need 1 more
    tier 1: last_played={3: 2, 4: 2, 5: 9}, 3 and 4 played long ago and tie, 5 played recently
    rng.shuffle                -> [3, 5, 4], random order first
    stable sort by last_played -> [3, 4, 5]  (3 and 4 tie at round 2, shuffle order survives; 5 sorts last)
    chosen.extend(candidates[:1]) -> chosen = [10, 3]
    """
    last_played = last_played or {}
    tiers = {}
    for candidate in pool:
        tiers.setdefault(times_played.get(candidate, 0), []).append(candidate)

    chosen = []
    for tier in sorted(tiers):
        # [:] shallow copy so shuffle doesn't alter tiers[tier]
        candidates = tiers[tier][:]
        rng.shuffle(candidates)
        # stable: ties keep the shuffle's order
        candidates.sort(key=lambda c: last_played.get(c, 0))
        chosen.extend(candidates[: needed - len(chosen)])
        if len(chosen) == needed:
            break
    return chosen


def _order_in_two_fronts(standings_order):
    """
    order player ids like: 1st, last, 2nd, 2nd-last, ..., converging toward the middle.

    standings_order: list[int]: player ids, strongest ranked first.
    returns: list[int]: every id from standings_order, reordered.

    example: standings_order=[1, 2, ..., 10] -> [1, 10, 2, 9, 3, 8, 4, 7, 5, 6]
    """
    order = []
    lo, hi = 0, len(standings_order) - 1
    while lo <= hi:
        order.append(standings_order[lo])
        if hi != lo:
            order.append(standings_order[hi])
        lo += 1
        hi -= 1
    return order


def _find_pool(standings_order, player_id, remaining):
    """
    candidates for player_id that still have an open slot, widening the window until at least one is found.

    standings_order: list[int]: player ids, strongest ranked first.
    player_id: int: the player to find candidates for.
    remaining: dict[int, int]: player id -> opponents still needed (0 means fully paired already).
    returns: list[int]: candidates with remaining > 0, possibly empty if nobody has an open slot at all.

    example: standings_order=[1, 2, ..., 30], player_id=15 (so pos=14), remaining={30: 1}, everyone else 0
    window_size=10 (half=5):  below = standings_order[15:20] = [16, ..., 20], 30 not in it
    window_size=20 (half=10): below = standings_order[15:25] = [16, ..., 25], 30 not in it
    window_size=30 (half=15): below = standings_order[15:30] = [16, ..., 30], 30 first appears here
    pool = [30]
    """
    window_size = INITIAL_WINDOW_SIZE
    pool = [c for c in get_pairing_window(standings_order, player_id, window_size) if remaining.get(c, 0) > 0]
    while not pool and window_size // 2 < len(standings_order) - 1:
        window_size += INITIAL_WINDOW_SIZE
        pool = [c for c in get_pairing_window(standings_order, player_id, window_size) if remaining.get(c, 0) > 0]
    return pool


def _repair_excluded_player(pairs, pos, player_id):
    """
    break the pair with the smallest worst-case distance to player_id (its farther member).
    reconnect both of its former partners to player_id.

    pairs: list[tuple[int, int]]: completed pairs so far; the selected one is replaced in place.
    pos: dict[int, int]: player id -> its index in the standings.
    player_id: int: the player with no candidates left; needs exactly 2 new opponents.

    example: pairs=[(10, 20), (6, 16)], player_id=11
    (10, 20): distance to 10 is 1, to 20 is 9, worst (max) of the two = 9
    (6, 16):  distance to 6 is 5, to 16 is 5, worst (max) of the two = 5
    (6, 16) has the lower worst-case, so it's replaced: pairs becomes [(10, 20), (11, 6), (11, 16)]
    """

    def get_worst_case_distance(i):
        """
        the larger of the two distances from player_id to pairs[i]'s members.

        i: int: index into pairs.
        returns: int: the worse (larger) of the two distances.
        """
        to_a = abs(pos[player_id] - pos[pairs[i][0]])
        to_b = abs(pos[player_id] - pos[pairs[i][1]])
        return max(to_a, to_b)

    # syntax: min_element = min(iterable, key=sorting_function)
    best = min(range(len(pairs)), key=get_worst_case_distance)
    a, b = pairs.pop(best)
    pairs.append((player_id, a))
    pairs.append((player_id, b))


def _find_any_duplicate(pairs):
    """
    return any duplicate pairing found: the same two players matched against each other twice.

    pairs: list[tuple[int, int]]: completed pairs.
    returns: tuple[int, int] | None: the duplicate pair, or None if there isn't one.
    """
    seen = set()
    for a, b in pairs:
        # immutable set is hashable
        key = frozenset((a, b))
        if key in seen:
            return a, b
        seen.add(key)
    return None


def _repair_duplicate(pairs, pos, a, b):
    """
    drop one copy of the (a, b) duplicate.
    find the pair, not involving a or b, whose members reconnect to a and b with the smallest worst-case distance.
    one former partner goes to a, the other to b.

    pairs: list[tuple[int, int]]: completed pairs, including the duplicate; modified in place.
    pos: dict[int, int]: player id -> its index in the standings.
    a: int: one of the two players paired with each other twice.
    b: int: the other.

    example: pairs=[(1, 2), (10, 20), (10, 20)], a=10, b=20
    dropping one (10, 20) leaves the candidate (1, 2)
    assignment 10-1, 20-2 (straight): worst = max(|10-1|, |20-2|) = max(9, 18) = 18
    assignment 10-2, 20-1 (crossed):  worst = max(|10-2|, |20-1|) = max(8, 19) = 19
    straight is better (18 < 19): pairs becomes [(10, 20), (10, 1), (20, 2)]
    """
    for i, (e, f) in enumerate(pairs):
        if {e, f} == {a, b}:
            pairs.pop(i)
            break

    def get_best_option_for_candidate(candidate_index):
        """
        the best worst-case distance for pairs[candidate_index].
        also whether "straight" achieves it, as opposed to "crossed".

        candidate_index: int: index into pairs.
        returns: tuple[int, bool]: the best worst-case distance, and whether straight is the better assignment.

        example: pairs=[(1, 2), (10, 20)], a=10, b=20, candidate_index=0 (so c=1, d=2)
        straight (10-1, 20-2): max(9, 18) = 18
        crossed (10-2, 20-1): max(8, 19) = 19
        returns (18, True)
        """
        c, d = pairs[candidate_index]
        a_c = abs(pos[a] - pos[c])
        b_d = abs(pos[b] - pos[d])
        straight = max(a_c, b_d)

        a_d = abs(pos[a] - pos[d])
        b_c = abs(pos[b] - pos[c])
        crossed = max(a_d, b_c)

        return min(straight, crossed), straight <= crossed

    # syntax: [output_expression for loop_vars in iterable if condition]
    candidates = [i for i, (e, f) in enumerate(pairs) if a not in (e, f) and b not in (e, f)]

    options = [(*get_best_option_for_candidate(i), i) for i in candidates]
    _, use_straight, best = min(options, key=lambda option: option[0])
    e, f = pairs.pop(best)

    if use_straight:
        pairs.append((a, e))
        pairs.append((b, f))
    else:
        pairs.append((a, f))
        pairs.append((b, e))


def build_round_pairings(standings_order, history, rng, last_played=None):
    """
    build one round's pairings using a two-fronts order: 1st, last, 2nd, 2nd last, ...
    the order converges toward the middle.

    for each player in that order still needing opponents: find candidates with _find_pool, pick via select_opponents.
    if _find_pool finds nobody with an open slot at all, _repair_excluded_player resolves it.
    afterward, _find_any_duplicate/_repair_duplicate clean up any pair that got matched against itself twice.

    standings_order: list[int]: active player ids, strongest ranked first, len >= MIN_ACTIVE_TO_START.
    history: dict[int, dict[int, int]]: player id -> {opponent id -> times already played}.
    rng: random.Random: source of randomness, passed through to select_opponents.
    last_played: dict[int, dict[int, int]] | None: player id -> {opponent id -> round most recently played}.
    returns: list[tuple[int, int]]: one round's matches; every player appears in exactly 2 pairs.
    """
    if len(standings_order) < MIN_ACTIVE_TO_START:
        raise ValueError("too_few_active_participants")

    last_played = last_played or {}
    order = _order_in_two_fronts(standings_order)
    pos = {player_id: i for i, player_id in enumerate(standings_order)}
    remaining = {player_id: 2 for player_id in standings_order}
    pairs = []

    for player_id in order:
        while remaining[player_id] > 0:
            pool = _find_pool(standings_order, player_id, remaining)

            # issue: excluded player. break the closest pair, reconnect both to this player.
            if not pool:
                _repair_excluded_player(pairs, pos, player_id)
                remaining[player_id] = 0
                continue

            opponents = select_opponents(
                pool, history.get(player_id, {}), remaining[player_id], rng, last_played.get(player_id, {})
            )

            for opponent in opponents:
                if remaining[player_id] == 0:
                    break
                remaining[player_id] -= 1
                remaining[opponent] -= 1
                pairs.append((player_id, opponent))

    # issue: players matched twice. break the closest unrelated pair to reconnect a duplicate
    duplicate = _find_any_duplicate(pairs)
    while duplicate:
        _repair_duplicate(pairs, pos, *duplicate)
        duplicate = _find_any_duplicate(pairs)

    return pairs
