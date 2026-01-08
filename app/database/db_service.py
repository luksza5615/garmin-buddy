import logging
import pandas as pd
import pyodbc
from app.database.db_connector import Database
from dataclasses import asdict
from sqlalchemy import text

logger = logging.getLogger(__name__)

class ActivityRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def check_if_activity_exists_in_db(self, activity_id):
        activities_rows_list = self.get_activity_ids()
        activities_ids_list = [row.activity_id for row in activities_rows_list]

        return activity_id in activities_ids_list

    def get_activities(self):
        query = "SELECT * FROM activity ORDER BY activity_start_time DESC"

        with self.database.get_db_connection() as conn:
            activities = pd.read_sql_query(query, conn)

        return activities

    def get_activity_ids(self):
        query = "SELECT activity_id FROM dbo.activity"

        with self.database.get_db_connection() as conn:
            activity_ids = conn.execute(
                text(query)
            ).fetchall()

        return activity_ids

    def get_db_activity_ids_set(self):
        rows = self.get_activity_ids()
        return set([row.activity_id for row in rows])
        
    def get_activities_last_x_days(self, days: int = 7):

        query = text("""
            SELECT * FROM activity 
            WHERE activity_start_time >= DATEADD(day, -:days, GETDATE())
            ORDER BY activity_start_time DESC
        """)

        with self.database.get_db_connection() as conn:
            result = conn.execute(query, {'days': days})
            activities = pd.DataFrame(result.fetchall(), columns=result.keys())
            number_of_activities = len(activities)
            logger.info("Found %d activities in the last %d days", number_of_activities, days)

        return activities

    def get_aggregated_data(self):
        query = """
            SELECT start_of_week, sum(distance_in_km) as suma
            FROM [dbo].[activity]
            GROUP BY start_of_week
            ORDER BY start_of_week desc
        """
        with self.database.get_db_connection() as conn:
            result = conn.execute(text(query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df
    
    def save_activity_to_db(self, activity):

        if self.check_if_activity_exists_in_db(activity.activity_id) is False:
            try:
                query = text("""INSERT INTO activity (
                            activity_id, activity_date, activity_start_time, sport, subsport, distance_in_km, elapsed_duration, 
                            grade_adjusted_avg_pace_min_per_km, avg_heart_rate, calories_burnt, aerobic_training_effect_0_to_5, 
                            anaerobic_training_effect_0_to_5, total_ascent_in_meters, total_descent_in_meters, start_of_week, running_efficiency_index)
                        VALUES (
                            :activity_id, :activity_date, :activity_start_time, :sport, :subsport, :distance_in_km, :elapsed_duration,
                            :grade_adjusted_avg_pace_min_per_km, :avg_heart_rate, :calories_burnt,
                            :aerobic_training_effect_0_to_5, :anaerobic_training_effect_0_to_5,
                            :total_ascent_in_meters, :total_descent_in_meters, :start_of_week, :running_efficiency_index)
                        """)

                # with database.engine.begin() as conn:
                #     conn.execute(query, activity_data_to_save_in_db)

                params = asdict(activity)

                with self.database.engine.begin() as conn:
                    conn.execute(query, params)

                logger.info("Activity %s_%s data saved in database sucessfully",
                    activity.sport, activity.activity_date)
            except pyodbc.ProgrammingError:
                logger.exception("Failed to save activity %s_%s due to error: %s", 
                    activity.sport, activity.activity_date)
        else:
            logger.info("Activity %s already exists in the database",
                (activity.activity_start_time))
