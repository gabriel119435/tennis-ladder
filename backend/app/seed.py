from sqlalchemy import select

from app.models import Match, Player, Ranking, RankingParticipant
from app.rounds import close_current_round, save_result, start_next_round
from app.scoring import VALID_SET_SCORES

# fmt: off
FIRST_NAMES = [
    "josé", "joão", "antônio", "francisco", "pedro", "carlos", "lucas", "luiz", "paulo", "gabriel",
    "maria", "ana", "francisca", "júlia", "antônia", "juliana", "adriana", "fernanda", "márcia", "patrícia",
]
LAST_NAMES = [
    "silva", "santos", "oliveira", "souza", "pereira", "ferreira", "lima", "alves", "rodrigues", "costa",
    "sousa", "gomes", "nascimento", "araújo", "ribeiro", "almeida", "jesus", "barbosa", "soares", "carvalho",
]
# fmt: on
DEFAULT_RANKING_NAME = "ranking de amostra"
ROUNDS = 15
# rng.choice needs a list, sorted keeps deterministic order from unordered set
SET_SCORES = sorted(VALID_SET_SCORES)


def seed_ranking(session, admin_id, rng):
    ranking = Ranking(name=DEFAULT_RANKING_NAME, created_by_admin_id=admin_id)
    session.add(ranking)
    participants = []
    for name in _random_names(rng):
        player = Player(name=name, created_by_admin_id=admin_id)
        session.add(player)
        session.flush()
        participant = RankingParticipant(ranking_id=ranking.id, player_id=player.id)
        session.add(participant)
        participants.append(participant)

    removed = rng.sample(participants, 4)

    for round_ in range(1, ROUNDS + 1):
        start_next_round(session, ranking, rng)
        session.flush()
        # fmt: off
        matches = session.scalars(
            select(Match).where(Match.ranking_id == ranking.id, Match.round == round_)
        ).all()
        # fmt: on
        last_round = round_ == ROUNDS

        if last_round:
            matches = rng.sample(matches, len(matches) // 2)

        for match, type_ in zip(matches, _result_types(len(matches), rng)):
            if type_ == "no_match":
                continue
            elif type_ == "walkover":
                save_result(
                    session,
                    match,
                    "walkover",
                    None,
                    rng.choice([match.player_a_id, match.player_b_id]),
                )
            else:
                save_result(
                    session,
                    match,
                    "played",
                    _random_sets(rng, type_ == "three_sets"),
                    None,
                )

        if not last_round:
            close_current_round(session, ranking)

        if round_ == 5:
            for participant in removed:
                participant.active = False
        if round_ == 8:
            for participant in rng.sample(removed, 2):
                participant.active = True


def _random_names(rng):
    # builds unique 'first last' names, each first and last name used once
    firsts = rng.sample(FIRST_NAMES, len(FIRST_NAMES))
    lasts = rng.sample(LAST_NAMES, len(LAST_NAMES))
    return [f"{first} {last}" for first, last in zip(firsts, lasts)]


def _result_types(count, rng):
    three_sets = max(1, int(count * 0.3))
    walkovers = max(1, int(count * 0.1))
    # fmt: off
    result_types = (
            ["three_sets"] * three_sets
            + ["walkover"] * walkovers
            + ["two_sets"] * (count - three_sets - walkovers)
    )
    # fmt: on

    rng.shuffle(result_types)

    result_types[rng.randrange(len(result_types))] = "no_match"
    return result_types


def _random_sets(rng, three_sets):
    first, second = rng.choice(SET_SCORES), rng.choice(SET_SCORES)
    if three_sets:
        third = rng.choice(SET_SCORES) if rng.random() < 0.5 else (10, rng.randint(0, 8))
        sets = [first, second[::-1], third]
    else:
        sets = [first, second]
    return sets if rng.random() < 0.5 else [set_[::-1] for set_ in sets]
