import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

def non_wear(df):
    # Calculate non-wear time using std if 2 of 3 axes is less than target, point can be marked as non-wear point

    df["Non_Wear"] =  df['SampleCounts'] == 0

    # mask the blocks for wear and non_wear time
    df['block'] = (df['Non_Wear'].astype(bool).shift() != df['Non_Wear'].astype(bool)).cumsum() # checks if next index label is different from previous
    df.assign(output=df.groupby(['block']).Time.apply(lambda x:x - x.iloc[0])) # calculate the time of each sample in blocks

    # times of blocks
    start_time_df = df.groupby(['block']).first() # start times of each blocked segment
    stop_time_df = df.groupby(['block']).last() # stop times for each blocked segment

    # lists of times stamps
    non_wear_starts_list=start_time_df[start_time_df['Non_Wear'] == True]['Time'].tolist()
    non_wear_stops_list=stop_time_df[stop_time_df['Non_Wear'] == True]['Time'].tolist()

    # new df from all non-wear periods
    data = { "Start": non_wear_starts_list, "Stop": non_wear_stops_list}
    df_non_wear=pd.DataFrame(data) # new df for non-wear start/stop times
    df_non_wear['Start'] = pd.to_datetime(df_non_wear['Start'], unit='s')  # convert timestamp to datetime object
    df_non_wear['Stop'] = pd.to_datetime(df_non_wear['Stop'], unit='s')  # convert timestamp to datetime object

    df_non_wear['Start'] = df_non_wear['Start'].dt.tz_localize('UTC').dt.tz_convert('America/Chicago')
    df_non_wear['Stop'] = df_non_wear['Stop'].dt.tz_localize('UTC').dt.tz_convert('America/Chicago')

    df_non_wear['delta'] = [pd.Timedelta(x) for x in (df_non_wear["Stop"]) - pd.to_datetime(df_non_wear["Start"])]

    # check if non-wear is longer than target
    valid_no_wear = df_non_wear["delta"] > datetime.timedelta(minutes=30) # greater than 30 minutes
    no_wear_timestamps=df_non_wear[valid_no_wear]

    return no_wear_timestamps