import zipfile
import os
import pandas as pd
import glob
from utils import progressBar
import numpy as np

def clean_and_sort(df):

    # print(df.head())
    df = df.apply(pd.to_numeric, errors='coerce')
    df.dropna(inplace=True)
    df.sort_values("Time", inplace=True)
    df.drop_duplicates(subset=['Time'], inplace=True)
    df = df[(df['Time'] > 1000000000000) & (df['Time'] < 10000000000000)]

    return df


def preprocess_data(wrist_directory, save_directory, participant):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    PPG_dfs = []
    Accel_dfs = []
    Gyro_dfs = []
    print("Combining Files")
    for _,_,files in os.walk(wrist_directory):
        #print(files)
        file_count = 0

        for file in progressBar(files, prefix = 'Progress:', suffix = 'Complete', length = 50):
            # print(file)
            try:
                wrist_files = os.path.join(wrist_directory, file)
                #print(wrist_files)
                archive = zipfile.ZipFile(wrist_files, 'r')
                archive_list = archive.namelist()
                file_count+=1
                for d in archive_list:
                    #print(d)
                    try:
                        if "PPG" in d:
                            wrist_data = archive.open(d)
                            # print("Reading PPG")
                            df = pd.read_csv(wrist_data, names=["Time", "ppg1", "ppg2"], skiprows=1, engine="python")
                            df = clean_and_sort(df)
                            PPG_dfs.append(df)
                        elif "Accelerometer" in d:
                            wrist_data = archive.open(d)
                            # print("Reading Accel")
                            df = pd.read_csv(wrist_data, names=["Time", "accX", "accY", "accZ"], skiprows=1, engine="python")
                            df = clean_and_sort(df)
                            Accel_dfs.append(df)
                        elif "Gyroscope" in d:
                            wrist_data = archive.open(d)
                            # print("Reading Gyro")
                            df = pd.read_csv(wrist_data, names=["Time", "rotX", "rotY", "rotZosboxe"], skiprows=1, engine="python")
                            df = clean_and_sort(df)
                            Gyro_dfs.append(df)
                    except:
                        pass
                        #print("----ERROR IN PANDAS READ----")
            except:
                pass
                # print("----ERROR IN PANDAS READ----")


        # print(PPG_df.head)
        ppg_csv_file = os.path.join(save_directory, 'PPG_{}.csv'.format(participant))
        PPG_df = pd.concat(PPG_dfs)
        PPG_df.to_csv(ppg_csv_file, index=False)
        # print(Accel_df.head)
        Accel_csv_file = os.path.join(save_directory, 'Accel_{}.csv'.format(participant))
        Accel_df = pd.concat(Accel_dfs)
        Accel_df.to_csv(Accel_csv_file, index=False)
        # print(Gyro_df.head)
        Gyro_csv_file = os.path.join(save_directory, 'Gyro_{}.csv'.format(participant))
        Gyro_df = pd.concat(Gyro_dfs)
        Gyro_df.to_csv(Gyro_csv_file, index=False)


if __name__ == '__main__':
    preprocess_data(999)