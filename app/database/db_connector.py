import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, before, after
from contextlib import contextmanager

load_dotenv()

db_connection_string = os.getenv("DB_CONNECTION_STRING")
engine = create_engine(db_connection_string, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(OperationalError),
    before=lambda rs: print(f"DB connection attempt #{rs.attempt_number}"),
    after=lambda rs: print(f"Attempt #{rs.attempt_number} finished")
)
def create_session_connection():
    session = SessionLocal()
    conn = session.connection()
    return session, conn


@contextmanager
def get_db_connection():
    session = None
    try:
        session, conn = create_session_connection()
        yield conn
    finally:
        if session:
            session.close()

# @contextmanager
# @retry(
#     stop=stop_after_attempt(5),
#     wait=wait_fixed(2),
#     retry=retry_if_exception_type(OperationalError),
#     before=lambda retry_state: print(f"Retrying connection... Attempt #{retry_state.attempt_number}"),
#     after=lambda retry_state: print(f"Attempt #{retry_state.attempt_number} finished"))
# def get_db_connection():
#     with SessionLocal() as session:
#         try:
#             conn = session.connection()
#             yield conn
#         except OperationalError as e:
#             print(f"Connection failed: {e}")
#             raise


def get_engine():
    return create_engine(db_connection_string, pool_pre_ping=True, connect_args={"timeout": 60})
