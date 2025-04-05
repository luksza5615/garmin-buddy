import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

db_connection_string = os.getenv("DB_CONNECTION_STRING")
engine = create_engine(db_connection_string, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_engine():
    return create_engine(db_connection_string, pool_pre_ping=True, connect_args={"timeout": 60})
