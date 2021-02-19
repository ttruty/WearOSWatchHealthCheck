#@title Calc reliability for accel meals


import os
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

def main():
    """
    Application entry point responsible for parsing command line requests
    """
    parser = argparse.ArgumentParser(description='Process wrist data from wear os watch.')

    parser.add_argument('input', metavar='input', type=str,
                        help='directory path for input')

    parser.add_argument('participant', metavar='part_id', type=str,
                        help='participant id')

    parser.add_argument('port', metavar='port', type=str, nargs='?', const="8050", default="8050",
                        help='port number to serve plotly')

    parser.add_argument('rate', metavar='rate', type=int, nargs='?', const=20, default=20,
                        help='sample rate of device')

    # parse command line arguments
    args = parser.parse_args()


    reliability_dict = {}

    #download only new data
    download_path = os.path.join(args.input, args.participant)
    download_data.download_data(args.participant, download_path)
    #preprocess data into single file
    output_path = os.path.join(args.input, "output")
    preprocessing.preprocess_data(args.participant, args.input, output_path)

    #load wrist data
    wrist_directory = os.path.join(output_path, args.participant)
    print(wrist_directory)
    for dirpath, _, filenames in os.walk(wrist_directory):
        print(filenames)
        accel_files = [f for f in filenames if 'Accel' in f]
        gyro_files = [f for f in filenames if 'Gyro' in f]
        ppg_files = [f for f in filenames if 'PPG' in f]

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

        df = pd.read_csv(os.path.join(wrist_directory, csv_files), engine='python')
        timeArr = df.iloc[:,0].values
        countDf = calc_reliability(timeArr, "second", wrist_directory, plot=0)

        # only calculate reliability with values from data, not interpolated for gaps
        pd.set_option('mode.chained_assignment', None)  # turn off warning for chained assignment. does not need saving
        recordedDataDf = countDf.loc[countDf['Interpolated'] == 0]
        recordedDataDf.loc[recordedDataDf["SampleCounts"] > args.rate, "SampleCounts"] = args.rate
        recordedDataDf['Reliability'] = recordedDataDf['SampleCounts'] / args.rate
        reliability_dict[sensor_name] = recordedDataDf["Reliability"].mean()
        #
        countDf['Time'] = pd.to_datetime(countDf['Time'], unit='s')
        countDf['Time'] = countDf['Time'].dt.tz_localize('UTC').dt.tz_convert('America/Chicago')

        # Reliability on plot
        # countDf.loc[countDf["SampleCounts"] > SAMPLE_RATE, "SampleCounts"] = SAMPLE_RATE
        # countDf['Reliability'] = countDf['SampleCounts'] / SAMPLE_RATE
        # reliability_dict[sensor_name] = countDf["Reliability"].mean()
        #
        # countDf['Time'] = pd.to_datetime(countDf['Time'], unit='s')
        # countDf['Time'] = countDf['Time'].dt.tz_localize('UTC').dt.tz_convert('America/Chicago')

        fig = px.line(countDf, x="Time", y="SampleCounts")
        figures.append(
            html.Div([
                html.H1(children='{} for {}'.format(sensor_name, args.participant)),
                dcc.Graph(
                    id='graph{}'.format(count),
                    figure=fig
                ),
            ])
        )
    app.layout = html.Div(children=figures)

    app.run_server(debug=False, port=args.port)


if __name__ == '__main__':
    main()