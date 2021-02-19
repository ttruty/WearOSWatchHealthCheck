import os

import pandas as pd
import pytz

settings = {}
settings['TIMEZONE'] = pytz.timezone('America/Chicago')


def df_to_datetime_tz_aware(in_df, column_list, timeUnit):
    from datetime import datetime, timedelta, date
    from six import string_types
    import numpy as np

    df = in_df.copy()

    for column in column_list:
        assert len(df) > 0  # if empty df, continue
        d = df[column].iloc[0]
        if isinstance(d, (int, np.int64)) or isinstance(d, (int, np.float)):
            df[column] = pd.to_datetime(df[column], unit=timeUnit, utc=True) \
                .dt.tz_convert(settings["TIMEZONE"])
        else:
            print('Cannot recognize the data type.')

    return df


def separate(watch_df, time_col, timeUnit, threshold):
    """
    Parameters:
        Required:
        - watch_df -- raw pandas data frame
        - time_col -- name of the time column (str)
        - timeUnit: ex. 'ms' (str)
        - threshold -- 0.005 for watch
    NOTE: the correct time offset has been -5 (Nov 2019 before daylight saving)
    """
    watch_df['Datetime'] = watch_df['Time']
    watch_df = df_to_datetime_tz_aware(watch_df, ['Datetime'], timeUnit)
    sqd = []
    everymin = []
    thismin = watch_df['Datetime'].iloc[0]

    while thismin < watch_df['Datetime'].iloc[len(watch_df['Datetime']) - 1]:
        nextmin = thismin + pd.DateOffset(minutes=1)
        temp = watch_df.loc[(watch_df['Datetime'] >= thismin) & (watch_df['Datetime'] < nextmin)].reset_index(drop=True)
        if len(temp) > 1:
            parta = temp[:len(watch_df['accX'])].reset_index(drop=True)
            partb = temp[1:].reset_index(drop=True)
            sum_sqd_diff = (partb['accX'] - parta['accX']) ** 2 + (partb['accY'] - parta['accY']) ** 2 + (
                        partb['accZ'] - parta['accZ']) ** 2
            sqd.append(sum_sqd_diff.mean())
            everymin.append(thismin)
        thismin = nextmin

    output = []
    for i in range(len(sqd)):
        if sqd[i] < threshold:
            output.append(0)
        else:
            output.append(1)

    watch_df.drop(['Datetime'], axis=1)

    return output, everymin


def get_weartime(watch_df, separate, time_col, timeUnit, threshold):
    """
    Parameters:
        Required:
        - watch_df -- raw pandas data frame
        - separate -- the function that returns the lables of raw data if every minute is above or below threshold
        - time_col -- name of the time column (str)
        - timeUnit -- ex. 'ms' (str)
        - threshold -- 0.005 for watch
    NOTE: the correct time offset has been -5 (Nov 2019 before daylight saving)
        Also need to go back and mark previous 3/60min as wear/notwear when switching states
    """
    labels, everymin = separate(watch_df, time_col, timeUnit, threshold)

    labels_after_rules = []
    count_wear = 0
    count_not_wear = 0
    count_append = 0
    check_wear = 0
    for i in labels:
        if i == 0:
            count_not_wear += 1
            count_wear = 0
            count_append += 1
            if count_not_wear >= 60:
                labels_after_rules += [0 for i in range(count_append)]
                count_append = 0
                check_wear = 0
        else:
            count_wear += 1
            count_not_wear = 0
            count_append += 1
            if count_wear >= 3:
                labels_after_rules += [1 for i in range(count_append)]
                count_append = 0
                check_wear = 1
    labels_after_rules += [check_wear for i in range(count_append)]

    return everymin, labels_after_rules


def test_get_weartime_logic():
    labels = [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1]
    print('total input minutes: ', len(labels))

    labels_after_rules = []
    count_wear = 0
    count_not_wear = 0
    count_append = 0
    check_wear = 0
    for i in labels:
        if i == 0:
            count_not_wear += 1
            count_wear = 0
            count_append += 1
            if count_not_wear >= 6:
                labels_after_rules += [0 for i in range(count_append)]
                count_append = 0
                check_wear = 0
        else:
            count_wear += 1
            count_not_wear = 0
            count_append += 1
            if count_wear >= 3:
                labels_after_rules += [1 for i in range(count_append)]
                count_append = 0
                check_wear = 1
    labels_after_rules += [check_wear for i in range(count_append)]

    print(labels_after_rules)
    print('total output minutes: ', len(labels_after_rules))


if __name__ == '__main__':
    #test_get_weartime_logic()
    wrist_directory = r"D:\HABitsLab\WristDataChecks\output\{}".format("503")
    for dirpath, _, filenames in os.walk(wrist_directory):
        csv_files = [f for f in filenames if 'Accel' in f]
        for csv_file in csv_files:
            print(csv_file)
            df = pd.read_csv(os.path.join(wrist_directory, csv_file), engine='python')
            everymin, labels_after_rules = get_weartime(df, separate, 'Time', 'ms', 0.005)
            print('total output minutes: ', len(labels_after_rules))
