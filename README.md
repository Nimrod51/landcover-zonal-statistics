# Zonal Landcover Statistics with CORINE Dataset

## Introduction
This Python script automates the process of visualizing the distribution of landcover leveraging the [CORINE Land Cover dataset](https://land.copernicus.eu/en/products/corine-land-cover) across different regions, using either a pie chart or a stacked bar chart. The script utilizes Plotly for interactive chart generation to explore landscape composition at various landcover aggregation levels. The flexibility of the script enables easy adaptation to different datasets and land cover categories, providing a powerful tool for quick land cover assessments and comparisons.

The workflow requires data preparation in QGIS __before__ running the script:

1. Load the input vector layer (zones) into QGIS, ensuring that there is a unique `NAME` field to differentiate the features.
2. Load the desired CORINE Land Cover dataset (e.g., the `.tif` file for 2018: `U2018_CLC2018_V2020_20u1.tif`).
3. Run the [Zonal Histogram](https://docs.qgis.org/3.34/en/docs/user_manual/processing_algs/qgis/rasteranalysis.html#zonal-histogram) tool.
4. Export the resulting output as a CSV file to be used in the script.

## Example Output

![sample plot](img/sample_plot.png "Example of the stacked bar plot generated by the script for Germany")

## Features
- **Interactive Stacked Bar Chart**: Visualizes the percentage of land cover categories per region.
- **Flexible Aggregation**: Supports different aggregation levels; these are generally "LABEL1", "LABEL2", or "LABEL3" and can be changed by modifying the `selected_label` variable.
- **Customizable Input**: Easily adjust the input CSV files for different datasets or land cover categories.
- **Consistent Color Scheme**: The script uses the **exact** colors specified in the [CORINE legend schema](https://www.eea.europa.eu/data-and-maps/data/corine-land-cover-2/corine-land-cover-classes-and/clc_legend.csv) for each land cover category. For coarser land cover categories, the __last__ color specified in the legend is used.

## System Requirements
- **QGIS 3**
- **Python 3.7+**  
- **Required Libraries**:
  - `pandas`
  - `plotly` (for interactive charts)
  - `matplotlib` (for additional plotting capabilities)
  - `matplotlib.patheffects` (for custom path effects)

You can install the required dependencies using `pip`:

```bash
pip install pandas plotly matplotlib