import pandas as pd
from app.database.db_connector import SessionLocal, get_db_connection
from app.services.garmin_service import download_activities, parse_and_save_file_to_db
from sqlalchemy import text


def get_activities():
    query = "SELECT * FROM activity_data ORDER BY activity_start_time DESC"

    with get_db_connection() as conn:
        activities = pd.read_sql_query(query, conn)
        print(activities)

    return activities


def get_top_activities():
    query = "SELECT TOP 10 * FROM activity_data ORDER BY activity_start_time DESC"

    with get_db_connection() as conn:
        activities = pd.read_sql_query(query, conn)
        print(activities)

    return activities


def get_activity_timestamps():
    query = "SELECT activity_start_time FROM dbo.activity_data"

    with get_db_connection() as conn:
        timestamps = conn.execute(
            text(query)
        ).fetchall()

    return timestamps


def get_latest_activity_date():
    query = "SELECT TOP 1 CONVERT(DATE, activity_start_time) AS LAST_DATE FROM dbo.activity_data ORDER BY activity_start_time DESC"

    with get_db_connection() as conn:
        return conn.execute(
            text(query)
        ).fetchone()[0]


def get_aggregated_data(agg_period):
    query = """
        SELECT start_of_week, sum(distance_in_km) as suma
        FROM [dbo].[activity_data]
        GROUP BY start_of_week
        ORDER BY start_of_week desc
    """

    with SessionLocal() as session:
        conn = session.connection()
        result = conn.execute(text(query))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df


def refresh_db():
    files = download_activities(refresh=True)

    for path in files:
        parse_and_save_file_to_db(path)


if __name__ == "__main__":
    refresh_db()
