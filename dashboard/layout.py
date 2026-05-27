import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dash_table, dcc, html
from contants import name_features
import dash_bootstrap_components as dbc


def get_layout(map_data: pd.DataFrame) -> html.Div:
    return html.Div(
        html.Div(
            html.Div(
                [
                    html.Div(
                        html.Div(
                            html.Div(
                                [
                                    html.Div(
                                        html.Div(
                                            create_table_container(map_data),
                                            className="border border-light-subtle border-2 rounded-4 p-2 bg-white",
                                            style={"height": "40vh"},
                                        ),
                                        className="col-12",
                                    ),
                                    html.Div(
                                        html.Div(
                                            create_graphs_container(),
                                            className="border border-light-subtle border-2 rounded-4 p-2 bg-white",
                                        ),
                                        className="col-12",
                                    ),
                                ],
                                className="row align-items gy-3",
                            ),
                            className="container overflow-hidden text-center h-100",
                        ),
                        className="col-6",
                    ),
                    html.Div(
                        html.Div(
                            create_map_container(),
                            className="border border-light-subtle border-2 rounded-4 p-2 bg-white",
                        ),
                        className="col-6",
                    ),
                ],
                className="row align-items gx-2",
            ),
            className="container-fluid text-center px-2",
        ),
        className="bg-light m-0 p-3 w-100 h-100",
    )


def create_map_container():
    return dcc.Graph(id="map", style={"height": "90vh"})


def create_table_container(map_data: pd.DataFrame):
    import dash_ag_grid as dag

    columnDefs = [
        {"field": "#étude", "sortable": False, "headerName": "ID Patient"},
        *[
            {"field": feature, "headerName": header, "filter": True}
            for feature, header in name_features.items()
        ],
    ]
    return [
        dag.AgGrid(
            id="sample-table",
            columnDefs=columnDefs,
            rowData=map_data.to_dict("records"),
            dashGridOptions={"pagination": True, "rowHeight": 20},
            columnSize="autoSize",
            style={"height": "100%", "width": "100%"},
            persistence=True,
        ),
        dcc.Store(id="filtered-data"),
    ]


def create_graphs_container():
    return html.Div(
        [
            dcc.Dropdown(
                options=[
                    {"label": feature_name, "value": feature}
                    for feature, feature_name in name_features.items()
                ],
                id="graph_feature",
                value="age",
            ),
            dcc.Graph(id="demographics", style={"height": "45vh"}),
        ]
    )
