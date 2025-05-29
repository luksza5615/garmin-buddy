import fitfile as ff
import os
from dotenv import load_dotenv

load_dotenv(override=True)

fit_file_path_test = os.getenv("FIT_FILE_PATH_TEST")


def list_all_fit_message_types(filepath):
    fitfile = ff.FitFile(filepath)
    message_summary = {}

    for message in fitfile.get_messages():
        msg_type = message.name
        if msg_type not in message_summary:
            message_summary[msg_type] = set()
        for field in message:
            message_summary[msg_type].add(field.name)

    # Convert sets to sorted lists for display
    for msg_type in message_summary:
        message_summary[msg_type] = sorted(list(message_summary[msg_type]))

    import pandas as pd
    df = pd.DataFrame.from_dict(message_summary, orient='index').transpose()
    return df


if __name__ == '__main__':
    # decode_fit(fit_file_path_test)
    list_all_fit_message_types(fit_file_path_test)
