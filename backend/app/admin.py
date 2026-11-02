import random

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app.db import get_session
from app.models import Admin, Match, Player, Ranking, RankingParticipant, SetScore
from app.seed import seed_ranking
from app.validation import name_error, password_error


def create_admin(username, password, seed=False):
    username = username.strip().lower()
    error = name_error(username) or password_error(password)
    if error:
        raise ValueError(error)

    try:
        with get_session(write=True) as session:
            admin = Admin(username=username, password_hash=generate_password_hash(password))
            session.add(admin)
            session.flush()
            if seed:
                seed_ranking(session, admin.id, random.Random())
        return True
    except IntegrityError:
        return False


def wipe_admin(session, admin_id):
    ranking_ids = select(Ranking.id).where(Ranking.created_by_admin_id == admin_id)
    match_ids = select(Match.id).where(Match.ranking_id.in_(ranking_ids))
    session.execute(delete(SetScore).where(SetScore.match_id.in_(match_ids)))
    session.execute(delete(Match).where(Match.ranking_id.in_(ranking_ids)))
    session.execute(delete(RankingParticipant).where(RankingParticipant.ranking_id.in_(ranking_ids)))
    session.execute(delete(Ranking).where(Ranking.created_by_admin_id == admin_id))
    session.execute(delete(Player).where(Player.created_by_admin_id == admin_id))
