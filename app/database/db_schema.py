from app.database.db_connector import SessionLocal
from sqlalchemy import text


def create_activity_table():
    query = """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='activity' AND xtype='U')
            CREATE TABLE activity (
                activity_id BIGINT NOT NULL PRIMARY KEY,
                activity_date DATE,
                activity_start_time DATETIME,
                sport VARCHAR(30),
                subsport VARCHAR(30),
                distance_in_km DECIMAL(5,2),
                elapsed_duration VARCHAR(10),
                grade_adjusted_avg_pace_min_per_km VARCHAR(255),
                avg_heart_rate INT,
                calories_burnt INT,
                aerobic_training_effect_0_to_5 DECIMAL(2,1),
                anaerobic_training_effect_0_to_5 DECIMAL(2,1),
                total_ascent_in_m INT,
                total_descent_in_m INT,
                start_of_week DATE,
                running_efficiency_index DECIMAL(5,2)
            )
            """

    with SessionLocal() as session:
        session.connection()
        connection = session.connection()
        connection.execute(text(query))
        connection.commit()
