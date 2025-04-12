from app.database.db_connector import SessionLocal
from sqlalchemy import text


def create_activity_table():
    query = """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='activity_data' AND xtype='U')
            CREATE TABLE activity_data (
                activity_date DATE,
                activity_start_time DATETIME PRIMARY KEY,
                sport VARCHAR(30),
                subsport VARCHAR(30),
                distance_in_km DECIMAL(5,2),
                elapsed_duration VARCHAR(10),
                grade_adjusted_avg_pace_min_per_km VARCHAR(255),
                avg_heart_rate INT,
                calories_burnt INT,
                aerobic_training_effect_0_to_5 DECIMAL(2,1),
                anaerobic_training_effect_0_to_5 DECIMAL(2,1),
                total_ascent_in_meters NT,
                total_descent_in_meters INT
            )
            """

    with SessionLocal() as session:
        session.connection()
        connection = session.connection()
        connection.execute(text(query))
        connection.commit()


def drop_table(table_name):
    query = f"DROP TABLE {table_name}"

    with SessionLocal() as session:
        connection = session.connection()
        connection.execute(text(query))
        connection.commit()


if __name__ == '__main__':
    create_activity_table()
    # drop_table("test")
