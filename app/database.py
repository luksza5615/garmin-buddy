import os
import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

db_login = os.getenv("DB_LOGIN")
db_password = os.getenv("DB_PASSWORD")
db_connection_string = os.getenv("DB_CONNECTION_STRING")

connection_url = URL.create(
    "mssql+pyodbc",
    username=db_login,
    password=db_password,
    host="ls-server.database.windows.net",
    port=1433,
    database="garmin",
    query={"driver": "ODBC Driver 18 for SQL Server",
           "Encrypt": "yes", "TrustServerCertificate": "yes"}
)


engine = create_engine(connection_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def connect_using_alchemy():
    engine = create_engine(connection_url)
    connection = engine.connect()
    print("Alchemy works")
    return engine


def connect_to_azuredb():
    connection = pyodbc.connect(db_connection_string)
    print("Azure DB connected")
    return connection


def get_engine():
    return create_engine(connection_url, pool_pre_ping=True, connect_args={"timeout": 60})


# connect_using_alchemy()
# connect_to_azuredb()
