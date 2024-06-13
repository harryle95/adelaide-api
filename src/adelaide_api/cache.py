from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from sqlalchemy.exc import NoResultFound
from sqlalchemy import JSON, create_engine, select
import datetime
from typing import Any
from requests import Response

__all__ = ("CacheTable", "CacheController", "session_factory")


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSON}


class CacheTable(Base):
    __tablename__ = "cache_table"
    query: Mapped[str] = mapped_column(primary_key=True)
    timestamp: Mapped[float] = mapped_column(
        default=datetime.datetime.now(datetime.UTC).timestamp()
    )
    response: Mapped[dict[str, Any]]

    def __repr__(self) -> str:
        return f"query: {self.query}, timestamp: {self.timestamp}"


engine = create_engine("sqlite:///db.sqlite")
Base.metadata.create_all(engine)
session_factory = sessionmaker(engine)


class CacheController:
    def __init__(
        self,
        stale_period: datetime.timedelta = datetime.timedelta(days=7),
    ) -> None:
        self.stale_period = stale_period

    def is_stale(self, data: CacheTable) -> bool:
        if data.timestamp is None:
            return False
        if datetime.datetime.now(datetime.UTC) - data.timestamp > self.stale_period:
            return True
        return False

    def get(self, session: Session, query: str) -> CacheTable | None:
        stmt = select(CacheTable).where(CacheTable.query == query)
        response = session.execute(stmt)
        try:
            ret_item = response.scalars().one()
            if self.is_stale(ret_item):
                return None
            return ret_item
        except NoResultFound:
            return None

    def set(self, session: Session, response: Response) -> None:
        cache_data = CacheTable(query=response.url, response=response.json())
        session.add(cache_data)
