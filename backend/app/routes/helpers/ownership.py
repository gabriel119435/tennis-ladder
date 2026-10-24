from flask import abort
from flask_login import current_user

from app.models import Ranking


def get_owned_ranking(session, ranking_id):
    ranking = session.get(Ranking, ranking_id)
    if not ranking:
        abort(404, "not_found")
    if ranking.created_by_admin_id != current_user.id:
        abort(403, "not_owner")
    return ranking
