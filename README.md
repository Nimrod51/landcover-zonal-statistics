# Landscape Distribution Plotting Script

## Introduction
This Python script provides an automated way to visualize the distribution of landscape categories from the [CORINE Land Cover dataset](https://land.copernicus.eu/en/products/corine-land-cover) across different regions, using a pie chart or a stacked bar chart. The script uses Plotly for interactive chart generation and allows users to explore landscape composition at various aggregation levels (e.g., by region, land cover type). The flexibility of the script enables easy adaptation to different datasets and land cover categories, offering a powerful tool for quick landcover assessments and comparisons. The workflow requires a data preparation step to be completed in QGIS prior to running the script: 

1. Load the input vector layer (zones) to QGIS; make sure there is a unique `NAME` field to differentiate the different features
2. Load the requested CORINE Landcover dataset (.tif file, for example for 2018 this is `U2018_CLC2018_V2020_20u1.tif`)
3. Run [Zonal Histogram](https://docs.qgis.org/3.34/en/docs/user_manual/processing_algs/qgis/rasteranalysis.html#zonal-histogram)
4. Export this output as CSV to be used in the script.


## Example output

![sample plot](img/sample_plot.png "Example of the stacked bar plot generated by the script for Germany")

## Features
- **Interactive Stacked Bar Chart**: Visualizes the percentage of land cover categories per region.
- **Flexible Aggregation**: Supports different aggregation levels (e.g., by land cover type or region).
- **Customizable Input**: Easily adjust the input CSV files for different datasets or land cover categories.
- **Consistent color scheme**: The script leverages the exact colors specified in the [CORINE legend schema](https://www.eea.europa.eu/data-and-maps/data/corine-land-cover-2/corine-land-cover-classes-and/clc_legend.csv) for each landcover category

## System Requirements
- **QGIS 3**
- **Python 3.7+**  
- **Libraries**:  
  - `pandas`
  - `plotly` (optional; for interactive charts)
  - `matplotlib` (for additional plotting capabilities)
  - `matplotlib.patheffects` (for custom path effects)
  You can install these dependencies using `pip`:
  ```bash
  pip install pandas plotly matplotlib