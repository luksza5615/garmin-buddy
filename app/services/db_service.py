import pandas as pd
from app.database import SessionLocal
from app.services.fit_parser import refresh_db


def get_activities():
    with SessionLocal() as session:
        conn = session.connection()
        query = """SELECT * FROM activity_data ORDER BY timestamp DESC"""
        activities = pd.read_sql_query(query, conn)
        return activities


def execute_azure(clear_database=False):
    # azure_connection = connect_to_azuredb()
    with SessionLocal() as session:
        conn = session.connection()

        if clear_database is True:
            conn.execute("""
                DROP TABLE activity_data""")

            conn.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='activity_data' AND xtype='U')
            CREATE TABLE activity_data (
                sport VARCHAR(30),
                subsport VARCHAR(30),
                timestamp DATETIME PRIMARY KEY,
                distance_km DECIMAL(5,2),
                elapsed_time VARCHAR(10),
                enhanced_avg_pace VARCHAR(255),
                avg_heart_rate INT,
                calories INT,
                aerobic_training_effect DECIMAL(2,1),
                anaerobic_training_effect DECIMAL(2,1),
                total_ascent INT,
                total_descent INT
            )
            """)
            conn.commit()

        refresh_db(conn)
