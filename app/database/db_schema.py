from app.database.db_connector import SessionLocal
from sqlalchemy import text


def create_activity_table():
    query = """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='activity_data' AND xtype='U')
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
