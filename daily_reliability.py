#@title Calc reliability for accel meals

import time
import datetime
import pandas as pd
import os
from calc_reliabilitly import calc_reliability
import pandas as pd

def calc(participant, sample_rate):
    reliability_dict = {}

    #load wrist data
    timestampCol = 1
    wrist_directory = r"D:\HABitsLab\WristDataChecks\output\{}".format(participant)
    for dirpath, _, filenames in os.walk(wrist_directory):
        accel_files = [f for f in filenames if 'Accel' in f]
        gyro_files = [f for f in filenames if 'Gyro' in f]
        ppg_files = [f for f in filenames if 'PPG' in f]


    sensor_data = [accel_files[0], gyro_files[0], ppg_files[0]]
    count = 0

    for sensor in sensor_data:
        count += 1
        if count == 1:
            sensor_name = "Accel"
        elif count == 2:
            sensor_name = "Gyro"
        elif count == 3:
            sensor_name = "PPG"

        df = pd.read_csv(os.path.join(wrist_directory, sensor), engine='python')
        timeArr = df.iloc[:,0].values
        countDf = calc_reliability(timeArr, "second", wrist_directory, plot=0)
        countDf.loc[countDf["SampleCounts"] > sample_rate, "SampleCounts"] = sample_rate
        countDf['Reliability'] = countDf['SampleCounts'] / sample_rate

        reliability_dict[sensor_name] = countDf["Reliability"].mean()

    return reliability_dict

if __name__ == '__main__':
    calc(503, 20)