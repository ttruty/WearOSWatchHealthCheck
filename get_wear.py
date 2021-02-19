import os
from datetime import datetime

import pandas as pd
from dateutil import tz
from calc_reliabilitly import calc_reliability
from collections import Counter

PARTICIPANT = 502


def get_wear(participant, file_path):
#load wrist data
    timestampCol = 1
    wrist_directory = os.path.join(file_path, participant)

    for dirpath, _, filenames in os.walk(wrist_directory):
        accel_files = [f for f in filenames if 'Accel' in f]

    df = pd.read_csv(os.path.join(wrist_directory, accel_files[0]), engine='python')

    timeArr = df.iloc[:, 0].values
    reliabDf = calc_reliability(timeArr, "second", os.path.join(wrist_directory, accel_files[0]), plot=0)
    reliabDf['Time'] = pd.to_datetime(reliabDf['Time'], unit='s')
    reliabDf['Time'] = reliabDf['Time'].dt.tz_localize('UTC').dt.tz_convert('America/Chicago')

    dateSeries = reliabDf.iloc[:, 0].dt.date
    datesCounter = Counter(dateSeries)
    counterDf = pd.DataFrame.from_dict(datesCounter, orient='index').reset_index()
    counterDf = counterDf.rename(columns={'index':'Date', 0:'Seconds'})
    counterDf['Hours'] = counterDf['Seconds'] / 60 / 60

    wear_time_file = os.path.join(wrist_directory, 'wear_time_{}.csv'.format(participant))
    counterDf.to_csv(wear_time_file, index=False)
    #print(counterDf)


if __name__ == '__main__':
    get_wear(500)