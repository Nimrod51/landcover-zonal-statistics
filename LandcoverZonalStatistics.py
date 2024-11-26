#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import matplotlib.patheffects as path_effects
import math

# Step 1: Load CSV files
zonal_histogram = pd.read_csv("data/zonal_histogram_portugal.csv")  # Zonal Histogram Output
clc_legend = pd.read_csv("data/clc_legend.csv")  # CLC Legend

# Step 2: Reshape Zonal Histogram for easy access
histogram_columns = [col for col in zonal_histogram.columns if col.startswith("HISTO_")]
zonal_histogram_long = zonal_histogram.melt(
    id_vars=["NAME"], value_vars=histogram_columns, var_name="HISTO", value_name="PixelCount"
)
zonal_histogram_long["GRID_CODE"] = zonal_histogram_long["HISTO"].str.extract(r"HISTO_(\d+)").astype(int)

# Merge with CLC Legend
zonal_histogram_long = zonal_histogram_long.merge(
    clc_legend[["GRID_CODE", "LABEL1", "LABEL2", "LABEL3"]],
    how="left", on="GRID_CODE"
)

# Step 3: Select aggregation level (using label)
selected_label = "LABEL2"  # Change to LABEL2 or LABEL3 as needed
zonal_histogram_long["SelectedLabel"] = zonal_histogram_long[selected_label]

# Step 4: Aggregate Data
aggregated_data = zonal_histogram_long.groupby(["NAME", "SelectedLabel"], as_index=False).agg({"PixelCount": "sum"})
aggregated_data = aggregated_data[aggregated_data["PixelCount"] > 0]

# Step 5: Ensure 'PixelPercentage' column exists
if "PixelPercentage" not in aggregated_data.columns:
    total_pixels_by_region = aggregated_data.groupby("NAME")["PixelCount"].transform("sum")
    aggregated_data["PixelPercentage"] = (aggregated_data["PixelCount"] / total_pixels_by_region) * 100

# Step 6: Plot Pie Charts (By Zone)
def plot_pie_charts(aggregated_data, unique_names):
    ncols = 3
    nrows = math.ceil(len(unique_names) / ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 5, nrows * 5))
    axes = axes.flatten()

    for idx, name in enumerate(unique_names):
        plot_data = aggregated_data[aggregated_data["NAME"] == name]
        plot_data = plot_data.groupby("SelectedLabel")["PixelCount"].sum()

        wedges, _, autotexts = axes[idx].pie(
            plot_data, autopct='%1.1f%%', startangle=90, pctdistance=0.8, shadow=True
        )
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
            autotext.set_color('black')
            autotext.set_path_effects([path_effects.withStroke(linewidth=2, foreground='white')])

        axes[idx].legend(
            wedges, plot_data.index, title="Categories", loc="upper left", bbox_to_anchor=(1, 0.5), fontsize=10
        )
        axes[idx].set_title(f"{name}", fontsize=12, pad=5)
        axes[idx].axis('equal')

    for idx in range(len(unique_names), len(axes)):
        fig.delaxes(axes[idx])

    plt.subplots_adjust(hspace=0.4, wspace=0.6)
    plt.savefig("output/combined_pie_charts.png", dpi=300, bbox_inches='tight')
    # plt.show()

# Plot pie charts
unique_names = aggregated_data["NAME"].unique()
plot_pie_charts(aggregated_data, unique_names)

# Step 7: Plot Stacked Bar Chart (Matplotlib)
def plot_stacked_bar_chart(aggregated_data, clc_legend, selected_label):
    unique_labels = aggregated_data["SelectedLabel"].unique()
    filtered_legend = clc_legend[clc_legend[selected_label].isin(unique_labels)]

    def parse_rgb(rgb_str):
        return tuple(int(c) / 255.0 for c in rgb_str.split("-"))
    
    filtered_legend["RGB_Tuple"] = filtered_legend["RGB"].apply(parse_rgb)
    label_to_color = dict(zip(filtered_legend[selected_label], filtered_legend["RGB_Tuple"]))

    pivot_data_percentage = aggregated_data.pivot(
        index="NAME", columns="SelectedLabel", values="PixelPercentage"
    ).fillna(0)

    colors = [label_to_color[label] for label in pivot_data_percentage.columns]

    fig, ax = plt.subplots(figsize=(12, 6))
    bottoms = pd.Series([0] * len(pivot_data_percentage), index=pivot_data_percentage.index)

    for idx, col in enumerate(pivot_data_percentage.columns):
        ax.bar(
            pivot_data_percentage.index, pivot_data_percentage[col],
            label=col, bottom=bottoms, color=colors[idx]
        )
        bottoms += pivot_data_percentage[col]

    plt.ylabel("Percentage (%)")
    plt.xlabel("Regions (NAME)")
    plt.title("Landcover Distribution Across Regions (%)")
    plt.legend(title="Land Cover Categories", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize="small")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig("output/stacked_bar_chart.png", dpi=300)
    # plt.show()

# Plot stacked bar chart
plot_stacked_bar_chart(aggregated_data, clc_legend, selected_label)

# Step 8: Plot Stacked Bar Chart (Plotly)
def plot_stacked_bar_chart_plotly(aggregated_data, clc_legend, selected_label):
    unique_labels = aggregated_data["SelectedLabel"].unique()
    filtered_legend = clc_legend[clc_legend[selected_label].isin(unique_labels)]

    def parse_rgb(rgb_str):
        return f"rgb({','.join(rgb_str.split('-'))})"

    filtered_legend["RGB_Tuple"] = filtered_legend["RGB"].apply(parse_rgb)
    label_to_color = dict(zip(filtered_legend[selected_label], filtered_legend["RGB_Tuple"]))

    pivot_data_percentage = aggregated_data.pivot(
        index="NAME", columns="SelectedLabel", values="PixelPercentage"
    ).fillna(0)

    fig = go.Figure()

    for label in pivot_data_percentage.columns:
        fig.add_trace(go.Bar(
            x=pivot_data_percentage.index, y=pivot_data_percentage[label],
            name=label, marker_color=label_to_color[label],
            hovertemplate="%{y:.2f}%",  # Format hover label with 1 decimal place and percentage sign
        ))

    fig.update_layout(
        height=700, width=1000, barmode='stack', title="Landscape Percentage Distribution Across Regions",
        xaxis_title="Regions (NAME)", yaxis_title="Percentage (%)", legend_title="Land Cover Categories",
        hovermode="x unified", template="plotly_white"
    )

    fig.show()

# Plot stacked bar chart (Plotly)
plot_stacked_bar_chart_plotly(aggregated_data, clc_legend, selected_label)