import os

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dash_table, dcc, html
from pyproj import Transformer

from layout import get_layout
import callbacks

from contants import name_features
def create_bar_chart(data: pd.DataFrame, feature: str) -> go.Figure:
    # Step 1: Aggregate counts by gender
    feature_counts = data.groupby(feature)["entity_count"].sum().sort_values(ascending=False).reset_index()
    if len(feature_counts) > 5:
        feature_counts = feature_counts.head(5)
    # Step 3: Create bar chart
    fig = go.Figure()

    for _, row in feature_counts.sort_values("entity_count", ascending=True).iterrows():
        fig.add_trace(
            go.Bar(
                y=[row[feature]],
                x=[row["entity_count"]],
                name=row[feature],
                text=[row["entity_count"]],
                textposition="auto",
                orientation='h'
            )
        )

    fig.update_layout(
        title=f"Répartition de {name_features[feature]} dans les données",
        yaxis_title=name_features[feature],
        xaxis_title="Nombre d'entités",
        template="simple_white",
        # legend_orientation="h",
        # legend_y=-0.5,
        # legend_x=0.5,
        # legend_xanchor="center",
        showlegend =False,
        font=dict(size=16),
        yaxis=dict(showgrid=False),
        xaxis=dict(showgrid=False),
    )

    fig.update_traces(marker_line_width=1.5, marker_line_color="black")

    return fig

def create_hist_chart(data: pd.DataFrame, feature: str) -> go.Figure:
    # Step 1: Aggregate counts by gender

    # Step 3: Create hist chart
    fig = px.histogram(data, x=feature)

    fig.update_layout(
        title=f"Répartition de {name_features[feature]} dans les données",
        xaxis_title=name_features[feature],
        yaxis_title="Nombre d'entités",
        template="simple_white",
        # legend_title=name_features[feature],
        font=dict(size=16),
        yaxis=dict(showgrid=False),
        xaxis=dict(showgrid=False),
    )

    fig.update_traces(marker_line_width=1.5, marker_line_color="black")

    return fig

