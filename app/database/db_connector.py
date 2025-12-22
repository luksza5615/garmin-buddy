import logging
from dataclasses import dataclass
from typing import Iterator
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, before, after
from sqlalchemy.exc import OperationalError
from contextlib import contextmanager
from app.config import Config

logger = logging.getLogger(__name__)

@dataclass
class Database:
    engine: Engine
    SessionLocal: sessionmaker
    
    @classmethod
    def create_db(cls, config: Config) -> "Database":
        engine = create_engine(config.db_connection_string, pool_pre_ping=True)
        SessionLocal = sessionmaker(bind=engine)

        return cls(
            engine=engine,
            SessionLocal=SessionLocal
        )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(OperationalError),
        before=lambda rs: logger.info(f"DB connection attempt #{rs.attempt_number}"),
        after=lambda rs: logger.info(f"Attempt #{rs.attempt_number} finished")
    )
    def create_session_connection(self):
        session = self.SessionLocal()
        conn = session.connection()
        return session, conn
    
    @contextmanager
    def get_db_connection(self) -> Iterator[object]:
        session: Session | None = None
        try:
            session, conn = self.create_session_connection()
            yield conn
        finally:
            if session is not None:
                session.close()

    def get_engine(self, config: Config) -> Engine:
        return self.engine


    
