import os
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()

garmin_login = os.getenv("GARMIN_EMAIL")
garmin_password = os.getenv("GARMIN_PASSWORD")


def login_to_garmin(email, password):
    garmin_connector = Garmin(email, password)
    garmin_connector.login()
    print("Connected to garmin")
    return garmin_connector


login_to_garmin(garmin_login, garmin_password)
