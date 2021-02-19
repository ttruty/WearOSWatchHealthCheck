import pandas as pd
#@title Calc reliability for accel meals
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import heartpy as hp
from scipy.signal import resample


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


withings_raw_file = r"C:\Users\Tim\Downloads\data_TIM_1613489620\raw_tracker_hr.csv"
wearos_raw_file = r"D:\HABitsLab\WristDataChecks\output\997\PPG_997.csv"

# Read withings file
withings_df = pd.read_csv(withings_raw_file, engine='python')
withings_df['start'] = pd.to_datetime(withings_df['start'], infer_datetime_format=True)
withings_df['value'] = withings_df['value'].map(lambda x: x.lstrip('[').rstrip(']'))
withings_df['value'] = withings_df['value'].astype(int)

# Read Wear os file
wearos_df = pd.read_csv(wearos_raw_file, engine='python')
wearos_df['Time'] = pd.to_datetime(wearos_df['Time'], unit='ms')


wearos_df['Time'] = wearos_df['Time'].dt.tz_localize('UTC').dt.tz_convert('America/Chicago')
wearos_df = wearos_df.sort_values('Time')
# wearos_df['Time'] = wearos_df['Time'].values.astype('<M8[s]') #truncate df time to seconds
# get sample rate of ppg wear os

filtered = hp.filter_signal(wearos_df["ppg1"], [0.7, 3.5], sample_rate=20,
                            order=3, filtertype='bandpass')
#resampled = resample(filtered, len(filtered) * 5)

#run HeartPy over it, fingers crossed
wd, m = hp.process_segmentwise(filtered, sample_rate = 20,
                   segment_width=30)

segments = m['segment_indices']
bpm = m['bpm']
heart_data = {'segments':segments,'bpm':bpm}
heart_df = pd.DataFrame(heart_data)
figures = []

df = pd.read_csv(wearos_raw_file, engine='python')

df = df.sort_values('Time')
df['Time'] = pd.to_datetime(df['Time'], unit='ms')
df['Time'] = df['Time'].dt.tz_localize('UTC').dt.tz_convert('America/Chicago')

withings_df = withings_df.sort_values('start')
fig = px.line(withings_df, x="start", y="value")
figures.append(
    html.Div([
        html.H1(children='Withings HR'),
        dcc.Graph(
            figure=fig
        ),
    ])
)

fig = px.line(heart_df, y="bpm")
figures.append(
    html.Div([
        html.H1(children='Withings HR'),
        dcc.Graph(
            figure=fig
        ),
    ])
)


app.layout = html.Div(children=figures)


if __name__ == '__main__':
    app.run_server(debug=False, port=8055)