#@title Calc reliability for accel meals


import os

import check_non_wear_time
from calc_reliabilitly import calc_reliability
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import download_data
import preprocessing
from get_wear import get_wear
from utils import progressBar
import sys
import argparse

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# D:\HABitsLab\WristDataChecks\output

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# parse command line arguments
parser = argparse.ArgumentParser(description='Process wrist data from wear os watch.')

parser.add_argument('input', metavar='input', type=str,
                    help='directory path for input')

parser.add_argument('participant', metavar='part_id', type=str,
                    help='participant id')

parser.add_argument('port', metavar='port', type=str, nargs='?', const="8050", default="8050",
                    help='port number to serve plotly')

parser.add_argument('rate', metavar='rate', type=int, nargs='?', const=20, default=20,
                    help='sample rate of device')


def main(args):
    """
    Application entry point responsible for parsing command line requests
    exaple command : python main.py D:\HABitsLab\WristDataChecks 511 [port] [sample count]
    """

    reliability_dict = {}

    #download only new data
    #download_path = os.path.join(args.input)
    #download_data.download_data(args.participant, download_path)

    #preprocess data into single file
    output_path = os.path.join(args.input, "../Aggregated", args.participant)
    preprocessing.preprocess_data(args.input, output_path, args.participant)

    #load wrist data
    print(output_path)
    for dirpath, _, filenames in os.walk(output_path):
        print(filenames)
        accel_files = [f for f in filenames if 'Accel' in f]
        gyro_files = [f for f in filenames if 'Gyro' in f]
        ppg_files = [f for f in filenames if 'PPG' in f]

    # only one file for each sensor in path
    sensor_data = [accel_files[0], gyro_files[0], ppg_files[0]]

    figures = []

    count = 0
    print("Generating Figure")
    for csv_files in progressBar(sensor_data, prefix = 'Progress:', suffix = 'Complete', length = 50):
        # for sensor in sensor_data:
        count += 1
        if count == 1:
            sensor_name = "Accel"
            get_wear(args.participant, output_path) # get wear time only from accel, only need 1 sensor
        elif count == 2:
            sensor_name = "Gyro"
        elif count == 3:
            sensor_name = "PPG"

        df = pd.read_csv(os.path.join(output_path, csv_files), engine='python')
        timeArr = df.iloc[:,0].values
        countDf = calc_reliability(timeArr, "second", output_path, plot=0)

        #get non wear time where sample count = 0 for greater than 30 minutes
        non_wear_timestamps = check_non_wear_time.non_wear(countDf)

        #convert timestamps to local time
        countDf['Time'] = pd.to_datetime(countDf['Time'], unit='s')
        countDf['Time'] = countDf['Time'].dt.tz_localize('UTC').dt.tz_convert('America/Chicago')

        # only calculate reliability with values from data, not interpolated for gaps
        pd.set_option('mode.chained_assignment', None)  # turn off warning for chained assignment. does not need saving

        # only capture wear periods for reliabilty score
        recordedDataDf = countDf
        for index, non_wear_segment in non_wear_timestamps.iterrows():
            recordedDataDf = recordedDataDf[(recordedDataDf['Time'] < non_wear_segment["Start"]) | (recordedDataDf['Time'] > non_wear_segment["Stop"])]

        recordedDataDf.loc[recordedDataDf["SampleCounts"] > args.rate, "SampleCounts"] = args.rate
        recordedDataDf['Reliability'] = recordedDataDf['SampleCounts'] / args.rate
        reliability_dict[sensor_name] = recordedDataDf["Reliability"].mean()

        # make plotly figure
        fig = px.line(countDf, x="Time", y="SampleCounts")
        for index, non_wear_segment in non_wear_timestamps.iterrows():
            fig.add_shape(type="rect",
                          xref="x",
                          yref="paper",
                          x0=non_wear_segment["Start"],
                          y0=0,
                          x1=non_wear_segment["Stop"],
                          y1=1,
                          line=dict(color="rgba(0,0,0,0)", width=3, ),
                          fillcolor="rgba(255,0,0,0.2)",
                          layer='below')
        figures.append(
            html.Div([
                html.H1(children='{} for {}'.format(sensor_name, args.participant)),
                html.H3(children="Reliability Average: {}".format(reliability_dict[sensor_name])),
                dcc.Graph(
                    id='graph{}'.format(count),
                    figure=fig
                ),
            ])
        )
    app.layout = html.Div(children=figures)
    app.run_server(debug=False, port=args.port)


if __name__ == '__main__':
    # sys.argv = ['main.py', 'D:\\HABitsLab\\WristDataChecks\\511', '511'] # DEBUGGING
    args = parser.parse_args()
    main(args)
