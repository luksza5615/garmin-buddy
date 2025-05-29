import os
import fitdecode
from dotenv import load_dotenv

load_dotenv(override=True)

fit_file_path_test = os.getenv("FIT_FILE_PATH_TEST")


def decode_fit(fit_file):
    with fitdecode.FitReader(fit_file) as fitfile:
        for frame in fitfile:
            if frame.frame_type == 0:  # 0 = DATA frame
                if frame.name == 'session':
                    primary_benefit = frame.get_value('training_effect_label')
                    if primary_benefit:
                        print('Primary Benefit:', primary_benefit)
                    else:
                        print('Primary Benefit: not found')


def decode_fit1(fit_file):
    print(fit_file)
    with fitdecode.FitReader(fit_file) as fitfile:
        for frame in fitfile:
            if frame.frame_type == 0:  # 0 = DATA frame
                if frame.name == 'session':
                    print('--- SESSION FOUND ---')
                    for field in frame.fields:
                        print(f'{field.name}: {field.value}')


if __name__ == '__main__':
    # decode_fit(fit_file_path_test)
    decode_fit1(fit_file_path_test)
