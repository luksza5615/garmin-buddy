import pandas as pd
from sqlalchemy import create_engine
# from app.database import connection_url, connect_to_azuredb
from app.database import SessionLocal
from app.services.fit_parser import refresh_db


def get_activities():
    # azure_cursor = azure_connection.cursor()
    # engine = create_engine(connection_url)
    with SessionLocal() as session:
        conn = session.connection()
        query = """SELECT * FROM activity_data ORDER BY timestamp DESC"""
        activities = pd.read_sql_query(query, conn)
        return activities


def execute_azure(refresh=True, clear_database=False):
    azure_connection = connect_to_azuredb()
    azure_cursor = azure_connection.cursor()

    if clear_database is True:
        azure_cursor.execute("""
            DROP TABLE activity_data""")

    # files = download_activities(azure_connection, True)

        azure_cursor.execute("""
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
        azure_connection.commit()

    # parse_and_save_single_file_to_db(fit_file_path_test, azure_connection)

    # parse_and_save_all_files_to_db(
    #     fit_dir_path, azure_connection)

    refresh_db(azure_connection)
