from typing import Counter
import pandas as pd
from app.services.garmin_service import download_activities, parse_and_save_file_to_db
from app.database.db_connector import Database
from sqlalchemy import text


def get_last_activity(database: Database):
    query = "SELECT TOP 1 * FROM activity ORDER BY activity_start_time DESC"

    with database.get_db_connection() as conn:
        activity = pd.read_sql_query(query, conn)
    print(activity)
    return activity




def get_activities(database: Database):
    query = "SELECT * FROM activity ORDER BY activity_start_time DESC"

    with database.get_db_connection() as conn:
        activities = pd.read_sql_query(query, conn)

    return activities


def get_top_activities(database: Database):
    query = "SELECT TOP 10 * FROM activity ORDER BY activity_start_time DESC"

    with database.get_db_connection() as conn:
        activities = pd.read_sql_query(query, conn)


    return activities


def get_activity_timestamps(database: Database): 
    query = "SELECT activity_start_time FROM dbo.activity"

    with database.get_db_connection() as conn:
        timestamps = conn.execute(
            text(query)
        ).fetchall()

    return timestamps

def get_activity_ids(database: Database):
    query = "SELECT activity_id FROM dbo.activity"

    with database.get_db_connection() as conn:
        activity_ids = conn.execute(
            text(query)
        ).fetchall()

    return activity_ids


def get_latest_activity_date(database: Database):
    query = "SELECT TOP 1 CONVERT(DATE, activity_start_time) AS LAST_DATE FROM dbo.activity ORDER BY activity_start_time DESC"

    with database.get_db_connection() as conn:
        return conn.execute(
            text(query)
        ).fetchone()[0]

def get_all_entries_temp(database: Database):
    query = "SELECT COUNT(*) FROM dbo.activity"

    with database.get_db_connection() as conn:
        return conn.execute(
            text(query)
        ).fetchone()[0]

def clear_db_temp(database: Database):
    query = "DELETE FROM dbo.activity"

    with database.get_db_connection() as conn:
        conn.execute(
            text(query)
        )
        conn.commit()
        return 


def get_activities_last_x_days(database: Database, days: int = 7):
    """
    Fetch activities from the last X days.
    
    Args:
        days (int): Number of days to look back (default: 7)
        
    Returns:
        pd.DataFrame: Activities data for the specified period
    """
    query = text("""
        SELECT * FROM activity 
        WHERE activity_start_time >= DATEADD(day, -:days, GETDATE())
        ORDER BY activity_start_time DESC
    """)

    with database.get_db_connection() as conn:
        result = conn.execute(query, {'days': days})
        activities = pd.DataFrame(result.fetchall(), columns=result.keys())
        print(f"Found {len(activities)} activities in the last {days} days")

    return activities


def get_aggregated_data(database: Database, agg_period):
    query = """
        SELECT start_of_week, sum(distance_in_km) as suma
        FROM [dbo].[activity]
        GROUP BY start_of_week
        ORDER BY start_of_week desc
    """
    with database.get_db_connection() as conn:
        result = conn.execute(text(query))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

def refresh_db():
    files = download_activities(refresh=True)

    for path in files:
        parse_and_save_file_to_db(path)


if __name__ == "__main__":
    from app.config import Config
    config = Config.from_env()
    database = Database.create_db(config)
    get_last_activity(database)
    # get_last_activity1(database)
    # refresh_db()
    # clear_db_temp()
    # counter= get_all_entries_temp()
    # print(counter)