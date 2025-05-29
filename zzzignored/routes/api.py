import pandas as pd
import simplejson as json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.database.db_connector import connect_to_azuredb


app = FastAPI()
connection_engine = connect_to_azuredb()


@app.get("/activities")
def get_activities():
    query = "SELECT TOP 10 * FROM activity_data ORDER BY timestamp desc"
    df = pd.read_sql(query, connection_engine)
    df['timestamp'] = df['timestamp'].astype(str)
    df = df.where(pd.notna(df), None)
    print(df)

    json_str = json.dumps(df.to_dict(orient="records"), ignore_nan=True)
    return JSONResponse(content=json.loads(json_str))


@app.get("/")
def home():
    print("API works on Azure correctlyyyy!!!")
    return {"message": "It worksssss!"}


# home()
