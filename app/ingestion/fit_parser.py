import logging
import fitparse

logger = logging.getLogger(__name__)


class FitParser:
    def __init__(self):
        pass

    def parse_fit_file(self, file_path):
        with open(file_path, "rb") as f:
            header_data = f.read(12)
            if header_data[8:12] != b".FIT":
                logger.exception("Invalid .fit file header: %s", file_path)

        logging.info(f"Parsing {file_path}...")
        fitfile = fitparse.FitFile(str(file_path))

        message_types = ["activity", "session"]  # most important: session

        parsed_activity = {}
        for message_type in message_types:
            for record in fitfile.get_messages(message_type):
                for field in record:
                    if field.name and field.value is not None:
                        parsed_activity[field.name] = field.value

        logging.debug("FULLY PARSED ACTIVITY DATA: \n %s \n", parsed_activity)

        return parsed_activity

    def print_message_data(self, message_type, file_path):
        print(f"Message type: {message_type}")
        fitfile = fitparse.FitFile(file_path)

        records = fitfile.get_messages(message_type)

        if not records:
            print(f"No records in message type {message_type}")

        for record in records:
            for record_field in record:
                # Print the records name and value (and units if it has any)
                if record_field.units:
                    print(
                        " * %s: %s %s"
                        % (
                            record_field.name,
                            record_field.value,
                            record_field.units,
                        )
                    )
                else:
                    print(" * %s: %s" % (record_field.name, record_field.value))

            print()

    def review_fit_file_fields(self, file_path):
        message_types = [
            "accelerometer_data",
            "activity",
            "ant_channel_id",
            "ant_rx",
            "ant_tx",
            "aviation_attitude",
            "barometer_data",
            "bike_profile",
            "blood_pressure",
            "cadence_zone",
            "camera_event",
            "capabilities",
            "connectivity",
            "course",
            "course_point",
            "device_info",
            "device_settings",
            "dive_alarm",
            "dive_gas",
            "dive_settings",
            "dive_summary",
            #  "event",
            "exd_data_concept_configuration",
            "exd_data_field_configuration",
            "exd_screen_configuration",
            "exercise_title",
            "field_capabilities",
            "file_capabilities",
            "file_creator",
            "goal",
            #  "gps_metadata",
            "gyroscope_data",
            "hr",
            "hr_zone",
            "hrm_profile",
            #  "lap",
            "length",
            "magnetometer_data",
            "memo_glob",
            "mesg_capabilities",
            "met_zone",
            "monitoring",
            "monitoring_info",
            "nmea_sentence",
            "obdii_data",
            "ohr_settings",
            "one_d_sensor_calibration",
            "power_zone",
            #  "record",
            "schedule",
            "sdm_profile",
            "segment_lap",
            "session",
            "set",
            "slave_device",
            "software",
            "speed_zone",
            "sport",
            "three_d_sensor_calibration",
            "timestamp_correlation",
            "totals",
            #  "user_profile",s
            "video",
            "video_clip",
            "video_description",
            "video_frame",
            "video_title",
            "watchface_settings",
            "weather_alert",
            "weather_conditions",
            "weight_scale",
            "workout",
            "workout_session",
            "workout_step",
            "zones_target",
        ]

        for message_type in message_types:
            self.print_message_data(message_type, file_path)
