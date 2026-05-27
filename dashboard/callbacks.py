import dash
import dash_ag_grid as dag
from dash import Dash, Input, Output, dcc, html, callback
import pandas as pd
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
from services.graphs import create_bar_chart, create_hist_chart
from collect_data import collect_and_clean_data

map_data = collect_and_clean_data(
    patient_location_file=contants.PATIENT_LOCATION_FILE,
    redcap_data_file=contants.REDCAP_DATA_FILE
)

@callback(
    Output("filtered-data", "data"),
    Input("sample-table", "filterModel"),
)
def get_cur_filter(selection_changed):
    if not selection_changed:
        return map_data.to_dict("records")
    print(selection_changed)
    filtered_data = map_data.copy()
    for column, filter_prop in selection_changed.items():
        if filter_prop["filterType"] == "text":
            if "operator" in filter_prop:
                if filter_prop["operator"] != "and":
                    for condition in filter_prop["conditions"]:
                        filtered_data = filter_text_with_props(
                            filtered_data, column, condition
                        )
                else:  # or
                    temp_filtered_data = pd.DataFrame()
                    for condition in filter_prop["conditions"]:
                        temp_filtered_data = pd.concat(
                            [
                                temp_filtered_data,
                                filter_text_with_props(
                                    filtered_data, column, condition
                                ),
                            ]
                        )
                    filtered_data = temp_filtered_data.drop_duplicates()
            else:
                filtered_data = filter_text_with_props(
                    filtered_data, column, filter_prop
                )
        if filter_prop["filterType"] == "number":
            if "operator" in filter_prop:
                if filter_prop["operator"] != "and":
                    for condition in filter_prop["conditions"]:
                        filtered_data = filter_number_with_props(
                            filtered_data, column, condition
                        )
                else:  # or
                    temp_filtered_data = pd.DataFrame()
                    for condition in filter_prop["conditions"]:
                        temp_filtered_data = pd.concat(
                            [
                                temp_filtered_data,
                                filter_number_with_props(
                                    filtered_data, column, condition
                                ),
                            ]
                        )
                    filtered_data = temp_filtered_data.drop_duplicates()
            else:
                filtered_data = filter_number_with_props(
                    filtered_data, column, filter_prop
                )
    print(filtered_data.head(5))
    return filtered_data.to_dict("records")


def filter_number_with_props(data: pd.DataFrame, column: str, filter_prop: dict):
    filter_value = filter_prop.get("filter")
    if filter_prop["type"] == "greaterThan":
        return data[data[column] > filter_value]
    if filter_prop["type"] == "lessThan":
        return data[data[column] < filter_value]
    if filter_prop["type"] == "greaterThanOrEqual":
        return data[data[column] >= filter_value]
    if filter_prop["type"] == "lessThanOrEqual":
        return data[data[column] <= filter_value]
    return data

def filter_text_with_props(data: pd.DataFrame, column: str, filter_prop: dict):
    filter_value = filter_prop.get("filter")
    if filter_prop["type"] == "contains":
        return data[data[column].str.contains(filter_value, case=False, na=False)]
    if filter_prop["type"] == "notContains":
        return data[~data[column].str.contains(filter_value, case=False, na=False)]
    if filter_prop["type"] == "blank":
        return data[data[column].isna() | (data[column] == "")]
    if filter_prop["type"] == "true":
        return data[data[column].fillna(False)]
    elif filter_prop["type"] == "false":
        return data[~data[column].astype(bool).fillna(True)]
    print("Unsupported filter type:", filter_prop["type"])
    return data

from contants import type_features
# Step 4: Callbacks
@callback(Output("demographics", "figure"), Input("filtered-data", "data"), Input("graph_feature", "value"))
def update_demographic_graph(selectedData, selected_feature: str):
    # Step 4: Aggregate entity counts per city
    data = pd.DataFrame.from_records(selectedData)
    if type_features[selected_feature] == "text":
        return create_bar_chart(data, feature=selected_feature)
    elif type_features[selected_feature] == "number":
        return create_hist_chart(data, feature=selected_feature)
    return create_bar_chart(data, feature="gender")


# Step 4: Callbacks
@callback(Output("map", "figure"), Input("filtered-data", "data"))
def update_dashboard(selectedData):
    # Map figure
    # Step 4: Aggregate entity counts per city
    data = pd.DataFrame.from_records(selectedData)
    city_stats = (
        data.groupby(["postal_code", "latitude", "longitude"], as_index=False)["#étude"]
        .count()
        .rename(columns={"#étude": "entity_count"})
    )
    # Step 4: Aggregate entity counts per city
    fig_map = px.scatter_map(
        city_stats,
        lat="latitude",
        lon="longitude",
        size="entity_count",
        color="entity_count",
        hover_name="postal_code",
        hover_data={"entity_count": True, "latitude": False, "longitude": False},
        color_continuous_scale="Viridis",
        size_max=30,
        zoom=6,
        map_style="carto-voyager",
    )

    fig_map.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        title={
            'text': "Nombre de patients par ville (taille et couleur des points)", 
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            "font": dict(size=20),
        },
        coloraxis_colorbar=dict(
            title=dict(text="Nombre d'entités", side="right"),
            thicknessmode="pixels", thickness=5,
            yanchor="top", y=1,
            ticks="outside",
            dtick=5
        )
    )
    return fig_map
