from garminconnect import Garmin


def login_to_garmin(email, password):
    try:
        garmin_connector = Garmin(email, password)
        garmin_connector.login()
        print("Connected to garmin")
        return garmin_connector
    except Exception as e:
        print(f"Failed to connect.{e}")
        raise
