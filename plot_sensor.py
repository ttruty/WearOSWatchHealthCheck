#@title Calc reliability for accel meals

import time
import datetime
import pandas as pd
import os
from calc_reliabilitly import calc_reliability
import matplotlib.pyplot as plt
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import datetime
import download_data
import preprocessing
from get_wear import get_wear
from utils import progressBar

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

PARTICIPANT = 997
SAMPLE_RATE = 20


#load wrist data
timestampCol = 1
wrist_directory = r"D:\HABitsLab\WristDataChecks\output\{}".format(PARTICIPANT)
for dirpath, _, filenames in os.walk(wrist_directory):
    accel_files = [f for f in filenames if 'Accel' in f]
    gyro_files = [f for f in filenames if 'Gyro' in f]
    ppg_files = [f for f in filenames if 'PPG' in f]

plots_list = []
count = 0

sensor_data = [accel_files[0], gyro_files[0], ppg_files[0]]
figures = []
count = 0

print("Generating Figure")
for csv_files in progressBar(sensor_data, prefix = 'Progress:', suffix = 'Complete', length = 50):
    # for sensor in sensor_data:
    count += 1
    if count == 1:
        sensor_name = "Accel"
        df = pd.read_csv(os.path.join(wrist_directory, csv_files), engine='python')
        df = df.sort_values('Time')

        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        df['Time'] = df['Time'].dt.tz_localize('UTC').dt.tz_convert('America/Chicago')

        fig = px.line(df, x="Time", y="accX")
        figures.append(
            html.Div([
                html.H1(children='{} for {}'.format(sensor_name, PARTICIPANT)),
                html.Div(
                    children="Sensor"),

                dcc.Graph(
                    id='graph{}'.format(count),
                    figure=fig
                ),
            ])
        )
    elif count == 2:
        sensor_name = "Gyro"
        df = pd.read_csv(os.path.join(wrist_directory, csv_files), engine='python')
        df = df.sort_values('Time')
        fig = px.line(df, x="Time", y="rotX")
        figures.append(
            html.Div([
                html.H1(children='{} for {}'.format(sensor_name, PARTICIPANT)),
                html.Div(
                    children="Sensor"),
                dcc.Graph(
                    id='graph{}'.format(count),
                    figure=fig
                ),
            ])
        )
    elif count == 3:
        sensor_name = "PPG"
        df = pd.read_csv(os.path.join(wrist_directory, csv_files), engine='python')
        df = df.sort_values('Time')
        fig = px.line(df, x="Time", y="ppg1")
        figures.append(
            html.Div([
                html.H1(children='{} for {}'.format(sensor_name, PARTICIPANT)),
                html.Div(
                    children="Sensor"),
                dcc.Graph(
                    id='graph{}'.format(count),
                    figure=fig
                ),
            ])
        )


app.layout = html.Div(children=figures)


if __name__ == '__main__':
    app.run_server(debug=False, port=8051)