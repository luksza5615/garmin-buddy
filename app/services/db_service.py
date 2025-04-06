import pandas as pd
from app.database.db_connector import SessionLocal
from app.services.fit_parser import download_activities, parse_and_save_single_file_to_db


def get_activities():
    query = """SELECT * FROM activity_data ORDER BY timestamp DESC"""

    with SessionLocal() as session:
        conn = session.connection()
        activities = pd.read_sql_query(query, conn)
        return activities


def refresh_db():
    with SessionLocal() as session:
        db_connection = session.connection()
        files = download_activities(db_connection, True)
        print(files)

    for path in files:
        parse_and_save_single_file_to_db(path, db_connection)


if __name__ == "__main__":
    refresh_db()
