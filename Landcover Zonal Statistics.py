#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import geopandas as gpd
# %matplotlib inline


# # Step 1: Read `Zonal Histogram` and `Legend` CSV files

# Two inputs are required:
# 
# 1. **Zonal histogram**: calculated using the CORINE Landcover and the overlayed vector zones. This layer MUST include a `NAME` field, in addition to the calculated `HISTO_{BAND_NUM}` fields. All other fields are ignored
# 2. **Corine Landcover Legend (CLC Legend)**: This is a CSV that was included in the original data, and includes all the labels and associated color values. https://land.copernicus.eu/en/products/corine-land-cover, https://www.eea.europa.eu/data-and-maps/data/corine-land-cover-2/corine-land-cover-classes-and/clc_legend.csv

# In[3]:


zonal_histogram = pd.read_csv("data/zonal_histogram_bundeslander.csv") # Zonal Histogram Output
clc_legend = pd.read_csv("/home/ngavish/Projects/_DATA/CORINE/clc_legend.csv") # 


# In[4]:


zonal_histogram.head()


# In[5]:


clc_legend.head()


# # Step 2: Map the zonal histogram to the CLC legend labels

# In[6]:


histogram_columns = [col for col in zonal_histogram.columns if col.startswith("HISTO_")]


# In[7]:


# Transpose and keep 'NAME' for context
zonal_histogram_long = zonal_histogram.melt(
    id_vars=["NAME"], 
    value_vars=histogram_columns,
    var_name="HISTO", 
    value_name="PixelCount"
)


# In[8]:


# Extract the numeric part of HISTO (e.g., HISTO_1 -> 1)
zonal_histogram_long["GRID_CODE"] = zonal_histogram_long["HISTO"].str.extract(r"HISTO_(\d+)").astype(int)


# In[9]:


# Merge the legend to include all labels
zonal_histogram_long = zonal_histogram_long.merge(
    clc_legend[["GRID_CODE", "LABEL1", "LABEL2", "LABEL3"]],
    how="left",
    on="GRID_CODE"
)


# In[10]:


zonal_histogram_long.head()


# # Step 3: Select aggregation level (using label) to be used for analysis 

# The CORINE dataset has generally three aggregation levels, ranging from `LABEL1 ` (most coarse) to `LABEL3` (most granular). Naturally, the level determines the number of landcover categories in the resulting plots. 

# In[11]:


selected_label = "LABEL2"  # Change to LABEL2 or LABEL3 as needed
zonal_histogram_long["SelectedLabel"] = zonal_histogram_long[selected_label]


# In[12]:


# Aggregation (Using SelectedLabel)
aggregated_data = (
    zonal_histogram_long
    .groupby(["NAME", "SelectedLabel"], as_index=False)
    .agg({"PixelCount": "sum"})
)


# In[13]:


# Drop records where PixelCount is 0
aggregated_data = aggregated_data[aggregated_data["PixelCount"] > 0]


# In[14]:


aggregated_data.head(20)


# # Plot Results as a Pie Chart (By Zone)

# In[15]:


import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import math

# Get unique names from the 'NAME' field
unique_names = aggregated_data["NAME"].unique()

# Define number of columns (adjust as needed)
ncols = 3  # Number of columns per row
nrows = math.ceil(len(unique_names) / ncols)  # Calculate the number of rows

# Create a single figure with subplots for all pie charts
fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols * 5, nrows * 5))

# Flatten axes array to loop over it easily
axes = axes.flatten()

# Loop through each unique name and generate the pie chart
for idx, name in enumerate(unique_names):
    # Filter data for the current 'NAME'
    plot_data = aggregated_data[aggregated_data["NAME"] == name]
    
    # Group by the selected label and summarize pixel counts
    plot_data = plot_data.groupby("SelectedLabel")["PixelCount"].sum()

    # Plot pie chart for this specific 'NAME'
    wedges, _, autotexts = axes[idx].pie(
        plot_data, 
        labels=None,  # No labels directly on the chart
        autopct='%1.1f%%', 
        startangle=90,
        pctdistance=0.8,  # Position percentages closer to the center
        shadow=True  # Add shadow for depth effect
    )

    # Add white outlines (masks) around the percentages
    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_weight('bold')
        autotext.set_color('black')
        autotext.set_path_effects([
            path_effects.withStroke(linewidth=2, foreground='white')  # Add white outline
        ])

    # Add legend for this specific pie chart, positioned outside
    axes[idx].legend(
        wedges, 
        plot_data.index, 
        title="Categories", 
        loc="upper left",  # Place legend to the upper left of the plot
        bbox_to_anchor=(1, 0.5),  # Position legend outside the chart area
        fontsize=10
    )

    # Set the title
    axes[idx].set_title(f"{name}", fontsize=12, pad=5)  # Reduce padding for title
    axes[idx].axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle.

# Remove empty subplots if there are any
for idx in range(len(unique_names), len(axes)):
    fig.delaxes(axes[idx])

# Adjust spacing between plots
plt.subplots_adjust(hspace=0.4, wspace=0.6)  # Add more horizontal space for legends

# Save and show the combined figure
output_file = "combined_pie_charts_legends_outside.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')

print(f"Combined pie charts with legends outside saved to '{output_file}'")
plt.show()


# # Stacked Bar Chart (using Matplotlib); exact colors from CORINE Legend

# In[16]:


import pandas as pd
import matplotlib.pyplot as plt

# Ensure clc_legend is loaded and available
# clc_legend = ...

# Example aggregated_data for demonstration
# aggregated_data = ...

# Step 1: Filter the clc_legend dataframe to match the labels present in aggregated_data
unique_labels = aggregated_data["SelectedLabel"].unique()
filtered_legend = clc_legend[clc_legend[selected_label].isin(unique_labels)]

# Step 2: Convert RGB values from clc_legend to matplotlib-compatible tuples
def parse_rgb(rgb_str):
    rgb = list(map(int, rgb_str.split("-")))
    return tuple(c / 255.0 for c in rgb)

filtered_legend["RGB_Tuple"] = filtered_legend["RGB"].apply(parse_rgb)

# Step 3: Create a mapping from SelectedLabel to RGB
label_to_color = dict(zip(filtered_legend[selected_label], filtered_legend["RGB_Tuple"]))

# Step 4: Handle PixelPercentage or calculate it if missing
if "PixelPercentage" not in aggregated_data.columns:
    total_pixels_by_region = aggregated_data.groupby("NAME")["PixelCount"].transform("sum")
    aggregated_data["PixelPercentage"] = (aggregated_data["PixelCount"] / total_pixels_by_region) * 100

# Pivot aggregated_data for stacked bar chart
pivot_data_percentage = aggregated_data.pivot(
    index="NAME", columns="SelectedLabel", values="PixelPercentage"
).fillna(0)

# Map colors to the labels in the pivot table
colors = [label_to_color[label] for label in pivot_data_percentage.columns]

# Step 5: Plot the stacked bar chart
fig, ax = plt.subplots(figsize=(12, 6))
bottoms = pd.Series([0] * len(pivot_data_percentage), index=pivot_data_percentage.index)
for idx, col in enumerate(pivot_data_percentage.columns):
    ax.bar(
        pivot_data_percentage.index,
        pivot_data_percentage[col],
        label=col,
        bottom=bottoms,
        color=colors[idx]
    )
    bottoms += pivot_data_percentage[col]

# Step 6: Customize plot appearance
plt.ylabel("Percentage (%)")
plt.xlabel("Regions (NAME)")
plt.title("Landcover Distribution Across Regions (%)")
plt.legend(title="Land Cover Categories", bbox_to_anchor=(1.05, 1), loc="upper left", fontsize="small")
plt.xticks(rotation=45)
plt.tight_layout()

# Save and show the plot
plt.savefig("stacked_bar_chart_with_correct_rgb_colors.png", dpi=300)
plt.show()


# # Stacked Bar Chart (using Plotly)

# In[17]:


import pandas as pd
import plotly.graph_objects as go

# Example aggregated_data and filtered_legend
# aggregated_data = ...
# filtered_legend = ...

# Step 1: Ensure `PixelPercentage` exists
if "PixelPercentage" not in aggregated_data.columns:
    total_pixels_by_region = aggregated_data.groupby("NAME")["PixelCount"].transform("sum")
    aggregated_data["PixelPercentage"] = (aggregated_data["PixelCount"] / total_pixels_by_region) * 100

# Step 2: Filter `filtered_legend` and match labels to colors
unique_labels = aggregated_data["SelectedLabel"].unique()
filtered_legend = clc_legend[clc_legend[selected_label].isin(unique_labels)]

def parse_rgb(rgb_str):
    rgb = list(map(int, rgb_str.split("-")))
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"

filtered_legend["RGB_Tuple"] = filtered_legend["RGB"].apply(parse_rgb)
label_to_color = dict(zip(filtered_legend[selected_label], filtered_legend["RGB_Tuple"]))

# Step 3: Pivot data for the stacked bar chart
pivot_data_percentage = aggregated_data.pivot(
    index="NAME", columns="SelectedLabel", values="PixelPercentage"
).fillna(0)

# Step 4: Create the interactive plot
fig = go.Figure()

for label in pivot_data_percentage.columns:
    fig.add_trace(go.Bar(
        x=pivot_data_percentage.index,
        y=round(pivot_data_percentage[label],1) ,
        name=label,
        marker_color=label_to_color[label],
        hoverinfo='x+y+name'  # Shows region, percentage, and label (e.g., "Arable land")
    ))

# Step 5: Customize layout
fig.update_layout(
    height=700,  # Adjust height to make the bars taller
    width=1000,   # Adjust width for better aspect ratio
    barmode='stack',
    title="Landscape Percentage Distribution Across Regions",
    xaxis_title="Regions (NAME)",
    yaxis_title="Percentage (%)",
    legend_title="Land Cover Categories",
    hovermode="x unified",  # Ensures hover info shows all stacked categories for a region
    template="plotly_white"
)


# Adjust figure layout to prevent squished bars
# fig.update_layout(
    
#     title=dict(x=0.5),  # Center the title
#     legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)  # Position the legend
# )



# Show the plot
fig.show()


# In[ ]:




