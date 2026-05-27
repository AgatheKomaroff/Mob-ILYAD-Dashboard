import os

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dash_table, dcc, html
from pyproj import Transformer

from layout import get_layout
import callbacks
import contants
from collect_data import collect_and_clean_data

map_data = collect_and_clean_data(
    patient_location_file=contants.PATIENT_LOCATION_FILE,
    redcap_data_file=contants.REDCAP_DATA_FILE
)


# Step 3: Dash dashboard
import dash_bootstrap_components as dbc
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

app.layout = get_layout(map_data)

if __name__ == "__main__":
    app.run(debug=True)
