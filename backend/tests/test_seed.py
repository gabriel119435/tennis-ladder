import random
from collections import Counter

from sqlalchemy import select

from app.db import get_session
from app.models import Match, Ranking, RankingParticipant
from app.seed import DEFAULT_RANKING_NAME, seed_ranking
from app.stats import compute_standings
from conftest import get_or_create_admin


def test_seed_ranking():
    admin_id = get_or_create_admin("admin1", "admin_pass1")
    with get_session(write=True) as session:
        seed_ranking(session, admin_id, random.Random(1))

    with get_session() as session:
        ranking = session.scalars(select(Ranking).where(Ranking.created_by_admin_id == admin_id)).one()
        matches = session.scalars(select(Match).where(Match.ranking_id == ranking.id)).all()
        participants = session.scalars(
            select(RankingParticipant).where(RankingParticipant.ranking_id == ranking.id)
        ).all()
        standings = compute_standings(session, ranking.id)

    assert (ranking.name, ranking.round, ranking.ongoing) == (DEFAULT_RANKING_NAME, 15, True)

    # 20 players, then 16 after 4 leave, then 18 after 2 come back
    matches_per_round = [sum(m.round == round_ for m in matches) for round_ in range(1, 16)]
    assert matches_per_round == [20, 20, 20, 20, 20, 16, 16, 16, 18, 18, 18, 18, 18, 18, 18]

    for round_ in range(1, 15):
        results = Counter(m.result_type for m in matches if m.round == round_)
        assert results[None] == 0
        assert results["no_match"] == 1

    # half of round 15 is picked (9), one of those is left empty, so 10 without a result
    assert sum(m.round == 15 and m.result_type is None for m in matches) == 10
    assert sum(p.active for p in participants) == 18

    # totals checked by hand against every match result, the 2 inactive players are left out
    keys = (
        "name",
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
    assert [tuple(row[key] for key in keys) for row in standings] == [
        ("francisco silva", 87, 19, 9, 29, 30, 42, 22, 312, 250),
        ("antônio souza", 80, 15, 12, 29, 30, 32, 29, 294, 261),
        ("gabriel pereira", 77, 15, 13, 29, 30, 35, 31, 293, 284),
        ("ana soares", 76, 15, 12, 28, 28, 33, 31, 275, 287),
        ("luiz almeida", 75, 14, 9, 26, 29, 30, 21, 264, 210),
        ("paulo sousa", 74, 14, 12, 28, 29, 30, 29, 248, 252),
        ("márcia alves", 71, 15, 13, 28, 29, 34, 31, 268, 265),
        ("patrícia santos", 70, 14, 14, 28, 29, 30, 30, 272, 265),
        ("joão costa", 60, 12, 12, 25, 30, 27, 28, 244, 252),
        ("júlia carvalho", 58, 13, 10, 23, 28, 27, 25, 248, 233),
        # tie on points: missed 2 (29-27), 2 (23-21) and 3 (28-25)
        # tie on missed: played 26 (9+17) vs 21 (12+9)
        ("maria araújo", 57, 9, 17, 27, 29, 23, 36, 245, 269),
        ("carlos oliveira", 57, 12, 9, 21, 23, 29, 19, 239, 187),
        ("lucas lima", 57, 11, 13, 25, 28, 29, 28, 245, 269),
        # tie on points: missed 4 (29-25), 5 (28-23)
        ("fernanda gomes", 54, 11, 14, 25, 29, 27, 31, 233, 274),
        ("adriana ferreira", 54, 10, 12, 23, 28, 23, 26, 220, 223),
        ("josé nascimento", 53, 11, 7, 19, 22, 24, 18, 209, 194),
        ("francisca ribeiro", 47, 8, 15, 24, 28, 21, 32, 218, 258),
        ("pedro rodrigues", 43, 7, 17, 25, 29, 18, 36, 211, 277),
    ]
