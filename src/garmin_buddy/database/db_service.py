from dataclasses import asdict
from datetime import date
import logging

import pandas as pd
import pyodbc
from sqlalchemy import text

from garmin_buddy.database.db_connector import Database

logger = logging.getLogger(__name__)


class ActivityRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get_activities(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> pd.DataFrame:
        if start_date is not None and end_date is not None and start_date > end_date:
            raise ValueError(
                f"Start date cannot be later than end date for activities range. Start date set: {start_date}, end date: {end_date}"
            )
        query_params: dict[str, date] = {}
        query = "SELECT * FROM [dbo].[activity] WHERE 1=1"

        if start_date is not None:
            query += " AND activity_date >= :start_date"
            query_params["start_date"] = start_date

        if end_date is not None:
            query += " AND activity_date <= :end_date"
            query_params["end_date"] = end_date

        with self.database.get_db_connection() as conn:
            activities = pd.read_sql_query(
                text(query), conn, params=query_params if query_params else None
            )

        logger.info("Fetched %d activities", len(activities))

        return activities

    def persist_activity(self, activity):
        if self._check_if_activity_exists_in_db(activity.activity_id) is False:
            try:
                query = text("""INSERT INTO activity (
                            activity_id, activity_date, activity_start_time, sport, subsport, distance_in_km, elapsed_duration, 
                            grade_adjusted_avg_pace_min_per_km, avg_heart_rate, calories_burnt, aerobic_training_effect_0_to_5, 
                            anaerobic_training_effect_0_to_5, total_ascent_in_m, total_descent_in_m, start_of_week, running_efficiency_index)
                            VALUES (
                            :activity_id, :activity_date, :activity_start_time, :sport, :subsport, :distance_in_km, :elapsed_duration,
                            :grade_adjusted_avg_pace_min_per_km, :avg_heart_rate, :calories_burnt,
                            :aerobic_training_effect_0_to_5, :anaerobic_training_effect_0_to_5,
                            :total_ascent_in_m, :total_descent_in_m, :start_of_week, :running_efficiency_index)
                        """)

                params = asdict(activity)

                with self.database.engine.begin() as conn:
                    conn.execute(query, params)

                logger.info(
                    "Activity %s_%s data saved in database sucessfully",
                    activity.sport,
                    activity.activity_date,
                )
            except pyodbc.ProgrammingError:
                logger.exception(
                    "Failed to save activity %s_%s due to error: %s",
                    activity.sport,
                    activity.activity_date,
                )
        else:
            logger.info(
                "Activity %s already exists in the database",
                (activity.activity_start_time),
            )

    def get_activity_ids_set(self):
        rows = self._get_activity_ids()

        return set([row.activity_id for row in rows])

    def _check_if_activity_exists_in_db(self, activity_id):
        activities_rows_list = self._get_activity_ids()
        activities_ids_list = [row.activity_id for row in activities_rows_list]

        return activity_id in activities_ids_list

    def _get_activity_ids(self):
        query = "SELECT activity_id FROM dbo.activity"

        with self.database.get_db_connection() as conn:
            activity_ids = conn.execute(text(query)).fetchall()

        return activity_ids
