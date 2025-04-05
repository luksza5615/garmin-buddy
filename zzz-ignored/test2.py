import os

from dotenv import load_dotenv

import requests

url = "https://my-garmin.azurewebsites.net/test"

try:
    response = requests.get(url)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
except requests.exceptions.RequestException as e:
    print("Request failed:", e)


db_connection_string = "Driver=ODBC Driver 18 for SQL Server;Server=tcp:ls-server.database.windows.net,1433;Database=garmin;Uid=lszata;Pwd=Exodus1@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
db_connection_string_alchemy = "mssql+pyodbc://lszata:Exodus1@@ls-server.database.windows.net:1433/garmin?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes"
fit_file_path_test = "C:\\Users\\SzataLukasz\\Documents\\Dysk Google\\Projects\\garmin-my\\fit_files\\2023-01-09_hiit_10275746736.fit"
fit_dir_path = "C:\\Users\\SzataLukasz\\Documents\\Dysk Google\\Projects\\garmin-my\\fit_files"

# load_dotenv()

# email = os.getenv("GARMIN_EMAIL")

# print(email)

# secret_key = os.getenv('MY_SECRET_KEY')
# if secret_key:
#     # Use the secret key as needed
#     print("Secret key retrieved successfully.")
# else:
#     print("Secret key not found. Ensure it's set in the environment variables.")
