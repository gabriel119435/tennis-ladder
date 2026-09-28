from dataclasses import dataclass

from flask_login import UserMixin
from sqlalchemy import Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


@dataclass
class AuthAdmin(UserMixin):  # session detached information about current database row
    id: int
    username: str
    password_hash: str


class Admin(UserMixin, Base):  # database row
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    created_by_admin_id: Mapped[int] = mapped_column(ForeignKey("admins.id"))

    __table_args__ = (UniqueConstraint("created_by_admin_id", "name"),)


class Ranking(Base):
    __tablename__ = "rankings"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    ongoing: Mapped[bool] = mapped_column(default=False)
    round: Mapped[int] = mapped_column(default=0)
    created_by_admin_id: Mapped[int] = mapped_column(ForeignKey("admins.id"))

    __table_args__ = (UniqueConstraint("created_by_admin_id", "name"),)


class RankingParticipant(Base):
    __tablename__ = "ranking_participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    ranking_id: Mapped[int] = mapped_column(ForeignKey("rankings.id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    active: Mapped[bool] = mapped_column(default=True)
    joined_at: Mapped[str]

    __table_args__ = (UniqueConstraint("ranking_id", "player_id"),)

    ranking = relationship("Ranking")
    player = relationship("Player")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    ranking_id: Mapped[int] = mapped_column(ForeignKey("rankings.id"))
    round: Mapped[int]
    player_a_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    player_b_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    result_type: Mapped[str | None] = mapped_column(Enum("played", "walkover", "no_match"))
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"))
    date: Mapped[str | None]

    __table_args__ = (
        Index("ix_matches_ranking_round", "ranking_id", "round"),
        Index("ix_matches_ranking_player_a", "ranking_id", "player_a_id"),
        Index("ix_matches_ranking_player_b", "ranking_id", "player_b_id"),
    )

    ranking = relationship("Ranking")
    player_a = relationship("Player", foreign_keys=[player_a_id])
    player_b = relationship("Player", foreign_keys=[player_b_id])
    winner = relationship("Player", foreign_keys=[winner_id])
    sets = relationship("SetScore", back_populates="match", order_by="SetScore.set_number")


class SetScore(Base):
    __tablename__ = "set_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    set_number: Mapped[int]
    games_a: Mapped[int]
    games_b: Mapped[int]

    __table_args__ = (UniqueConstraint("match_id", "set_number"),)

    match = relationship("Match", back_populates="sets")
