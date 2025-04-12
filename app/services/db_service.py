import pandas as pd
from app.database.db_connector import SessionLocal
from app.services.garmin_service import download_activities, parse_and_save_single_file_to_db
from sqlalchemy import text


def get_activities():
    query = "SELECT * FROM activity_data ORDER BY activity_start_time DESC"

    with SessionLocal() as session:
        conn = session.connection()
        activities = pd.read_sql_query(query, conn)
        print(activities)
        return activities


def get_latest_activity_date():
    query = "SELECT TOP 1 CONVERT(DATE, activity_start_time) AS LAST_DATE FROM dbo.activity_data ORDER BY activity_start_time DESC"

    with SessionLocal() as session:
        conn = session.connection()
        return conn.execute(
            text(query)
        ).fetchone()[0]


def refresh_db():
    files = download_activities(refresh=True)

    for path in files:
        parse_and_save_single_file_to_db(path)


if __name__ == "__main__":
    # get_activities()
    refresh_db()
