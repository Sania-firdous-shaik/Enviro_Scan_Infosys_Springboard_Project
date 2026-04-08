# 🌍 Interactive Dashboard Development and System Integration


[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Folium](https://img.shields.io/badge/Folium-Latest-green.svg)](https://python-visualization.github.io/folium/)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-Latest-orange.svg)](https://geopandas.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📘 Overview

This module transforms **raw pollution data and ML predictions** into **interactive geospatial visualizations**. By integrating **Folium** and **GeoPandas**, it creates **dynamic pollution heatmaps** that enable users to explore **source-specific insights** and **high-risk zones** through an intuitive map interface.

The system empowers environmental authorities and researchers to:
- 🗺️ **Visualize pollution sources** on interactive maps
- 🔥 **Identify hotspots** through heatmap overlays
- 🎯 **Track pollution patterns** across regions
- 📊 **Support data-driven decisions** for environmental policy

---

## 🎯 Key Objectives

- ✅ Visualize **pollution source predictions** on an interactive map interface
- ✅ Display **heatmaps** based on pollutant severity (PM2.5, PM10, etc.)
- ✅ Add **source-specific markers** (🏭 Industrial, 🚗 Vehicular, 🏠 Residential, 🌾 Agricultural, 🌿 Natural)
- ✅ Enable **filtering by date, location, or source category**
- ✅ Integrate visual maps into the **AI-EnviroScan dashboard** for real-time analysis

---

## ⚙️ Workflow

### 1️⃣ Load Predictions and Geospatial Data

Import pollution data with model predictions and location coordinates:

```python
import pandas as pd

# Load predicted results
predictions = pd.read_csv('pollution_data_all_india_enhanced.csv')
print(predictions.head())
```

**Expected Data Structure:**

| Column | Description | Example |
|--------|-------------|---------|
| `city` | City name | Mumbai |
| `latitude` | Latitude coordinate | 19.0760 |
| `longitude` | Longitude coordinate | 72.8777 |
| `pollution_source` | Predicted source | Industrial |
| `pm25` | PM2.5 concentration | 85.3 |
| `pm10` | PM10 concentration | 120.5 |
| `date` | Measurement date | 2025-10-15 |

---

### 2️⃣ Create Interactive Map

Initialize a Folium map centered on your region of interest:

```python
import folium

# Initialize base map (centered on India as example)
m = folium.Map(
    location=[20.5937, 78.9629],  # Center coordinates
    zoom_start=5,
    tiles='CartoDB positron'
)
```

**Available Tile Options:**
- `OpenStreetMap` - Default street map
- `CartoDB positron` - Clean, light background
- `CartoDB dark_matter` - Dark theme
- `Stamen Terrain` - Topographic view

---

### 3️⃣ Plot Source-Specific Markers

Add distinct visual markers for each pollution source category:

```python
# Define source-specific icons
source_icons = {
    'Industrial': '🏭',
    'Vehicular': '🚗',
    'Residential': '🏠',
    'Agricultural': '🌾',
    'Natural': '🌿'
}

# Add markers to map
for _, row in predictions.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"""
            <b>City:</b> {row['city']}<br>
            <b>Source:</b> {row['pollution_source']}<br>
            <b>PM2.5:</b> {row['pm25']} µg/m³<br>
            <b>Date:</b> {row['date']}
        """,
        icon=folium.DivIcon(
            html=f"<div style='font-size:24px;'>{source_icons.get(row['pollution_source'], '❓')}</div>"
        )
    ).add_to(m)
```

**Marker Categories:**
- 🏭 **Industrial** - Factories, manufacturing plants
- 🚗 **Vehicular** - Traffic emissions, transportation
- 🏠 **Residential** - Household activities, heating
- 🌾 **Agricultural** - Crop burning, farming activities
- 🌿 **Natural** - Dust storms, wildfires

---

### 4️⃣ Generate Pollution Heatmap

Visualize pollutant intensity using a heat map overlay:

```python
from folium.plugins import HeatMap

# Prepare heat data [latitude, longitude, intensity]
heat_data = [
    [row['latitude'], row['longitude'], row['pm25']] 
    for _, row in predictions.iterrows()
]

# Add heatmap layer
HeatMap(
    heat_data,
    radius=12,        # Size of heat radius
    blur=20,          # Blur effect
    max_zoom=6,       # Maximum zoom level
    gradient={        # Custom color gradient
        0.0: 'blue',
        0.5: 'yellow',
        1.0: 'red'
    }
).add_to(m)
```

**Heatmap Parameters:**
- `radius` - Controls the size of each heat point
- `blur` - Smoothness of the gradient
- `max_zoom` - Visibility at different zoom levels
- `gradient` - Custom color mapping for intensity

---

### 5️⃣ Visualize High-Risk Zones

Add color-coded circle markers to indicate severity levels:

```python
def get_color(value):
    """Return color based on pollution level"""
    if value > 150:
        return 'red'      # High pollution
    elif value > 80:
        return 'orange'   # Moderate pollution
    else:
        return 'green'    # Low pollution

def get_radius(value):
    """Scale circle size by pollution level"""
    return value / 3

# Add circle markers with severity colors
for _, row in predictions.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=get_radius(row['pm25']),
        color=get_color(row['pm25']),
        fill=True,
        fillColor=get_color(row['pm25']),
        fillOpacity=0.6,
        popup=f"{row['city']}: {row['pm25']} µg/m³"
    ).add_to(m)
```

**Pollution Level Classification:**
- 🟩 **Low** (0-80 µg/m³) - Good air quality
- 🟧 **Moderate** (81-150 µg/m³) - Acceptable air quality
- 🟥 **High** (151+ µg/m³) - Unhealthy air quality

---

### 6️⃣ Add Filtering Options

Enable dynamic filtering for focused analysis:

```python
# Filter by pollution source
def filter_by_source(data, source):
    return data[data['pollution_source'] == source]

# Filter by date range
def filter_by_date(data, start_date, end_date):
    data['date'] = pd.to_datetime(data['date'])
    return data[(data['date'] >= start_date) & (data['date'] <= end_date)]

# Filter by pollution threshold
def filter_by_threshold(data, pollutant='pm25', threshold=100):
    return data[data[pollutant] > threshold]

# Example: Visualize only vehicular pollution
vehicular_data = filter_by_source(predictions, 'Vehicular')

# Example: High pollution areas only
high_pollution = filter_by_threshold(predictions, 'pm25', 150)
```

**Filtering Capabilities:**
- 📅 **By Date** - Time series analysis
- 📍 **By Location** - Regional focus
- 🏷️ **By Source** - Category-specific insights
- 📊 **By Threshold** - Severity-based filtering

---

### 7️⃣ Export Interactive Map

Save the map for dashboard integration or web embedding:

```python
# Save map as HTML
m.save('pollution_heatmap.html')
print("✅ Map exported successfully as 'pollution_heatmap.html'")

# Optional: Display in Jupyter Notebook
from IPython.display import IFrame
IFrame('pollution_heatmap.html', width=1000, height=600)
```

**Export Options:**
- HTML file for web embedding
- Jupyter Notebook display
- Dashboard integration
- Standalone web application

---

## 📈 Visualization Features

### ✅ Heatmap Layer
- Shows pollution intensity across cities and regions
- Dynamic color gradients from blue (low) to red (high)
- Adjustable radius and blur effects

### ✅ Source Markers
- Icon-based representation of pollution sources
- Interactive popups with detailed information
- Category filtering for focused analysis

### ✅ Interactive Filtering
- Explore by date, category, or city
- Real-time data updates
- Custom threshold settings

### ✅ Exportable HTML Map
- Integrates directly into dashboard UI
- Embeddable in web applications
- Shareable with stakeholders

---

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Dependencies

Install required packages:

```bash
pip install folium geopandas pandas numpy matplotlib
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
folium>=0.12.0
geopandas>=0.10.0
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
branca>=0.4.0
```

---

## 🚀 Usage

### Complete Workflow Example

```python
import pandas as pd
import folium
from folium.plugins import HeatMap

# 1. Load data
predictions = pd.read_csv('predicted_pollution_sources.csv')

# 2. Initialize map
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles='CartoDB positron')

# 3. Add markers
source_icons = {
    'Industrial': '🏭', 'Vehicular': '🚗', 'Residential': '🏠',
    'Agricultural': '🌾', 'Natural': '🌿'
}

for _, row in predictions.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"City: {row['city']}<br>Source: {row['pollution_source']}",
        icon=folium.DivIcon(html=f"<div style='font-size:24px;'>{source_icons[row['pollution_source']]}</div>")
    ).add_to(m)

# 4. Add heatmap
heat_data = [[row['latitude'], row['longitude'], row['pm25']] for _, row in predictions.iterrows()]
HeatMap(heat_data, radius=12, blur=20, max_zoom=6).add_to(m)

# 5. Save map
m.save('pollution_heatmap.html')
print("✅ Map created successfully!")
```

### Advanced Customization

```python
# Add layer control for toggling features
from folium import FeatureGroup, LayerControl

# Create feature groups
markers_group = FeatureGroup(name='Pollution Sources')
heatmap_group = FeatureGroup(name='Heatmap')
circles_group = FeatureGroup(name='Severity Zones')

# Add features to respective groups
# ... (add markers, heatmap, circles)

# Add groups to map
markers_group.add_to(m)
heatmap_group.add_to(m)
circles_group.add_to(m)

# Add layer control
LayerControl().add_to(m)
```

---

## 📊 Output Files

| File | Description | Usage |
|------|-------------|-------|
| `pollution_heatmap.html` | Interactive pollution heatmap | Embed in dashboard or share via web |
| `predicted_pollution_sources.csv` | Input data with model predictions | Data source for visualization |
| `geo_visualization.ipynb` | Jupyter notebook for map creation | Development and experimentation |
| `Maps/` | Folder for map assets | Icons, legends, custom markers |

---

## 🧩 Integration with AI-EnviroScan Dashboard

### Dashboard Embedding

```python
import streamlit as st
import streamlit.components.v1 as components

# Display map in Streamlit dashboard
def display_pollution_map():
    with open('pollution_heatmap.html', 'r', encoding='utf-8') as f:
        map_html = f.read()
    components.html(map_html, height=600)

# Streamlit app
st.title("🌍 AI-EnviroScan Pollution Map")
display_pollution_map()
```

### Real-Time Updates

```python
# Update map with new predictions
def update_map(new_predictions):
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    # Add updated markers and heatmap
    # ...
    m.save('pollution_heatmap.html')
    return m
```

### Dashboard Features
- 📍 **Interactive hotspot identification**
- 📊 **Real-time pollution tracking**
- 🎯 **Source-wise analysis**
- 🚨 **Alert system for high-risk zones**
- 📈 **Trend analysis over time**

---

## 🎨 Customization Options

### Color Schemes

```python
# Custom color palette for different sources
source_colors = {
    'Industrial': '#FF5733',     # Red
    'Vehicular': '#FFC300',      # Yellow
    'Residential': '#28A745',    # Green
    'Agricultural': '#8B4513',   # Brown
    'Natural': '#4CAF50'         # Light Green
}
```

### Map Styles

```python
# Different base map styles
tiles_options = [
    'OpenStreetMap',
    'CartoDB positron',
    'CartoDB dark_matter',
    'Stamen Terrain',
    'Stamen Toner'
]
```

### Icon Customization

```python
# HTML-based custom icons
custom_icon = folium.DivIcon(html=f"""
    <div style="
        font-size: 20px;
        color: white;
        background-color: red;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        text-align: center;
        line-height: 30px;
    ">🏭</div>
""")
```

---

## 📈 Performance Optimization

### Large Dataset Handling

```python
# Use MarkerCluster for many points
from folium.plugins import MarkerCluster

marker_cluster = MarkerCluster().add_to(m)

for _, row in predictions.iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"{row['city']}"
    ).add_to(marker_cluster)
```

### Efficient Heatmap Generation

```python
# Sample data for better performance
if len(predictions) > 1000:
    sampled_data = predictions.sample(1000)
else:
    sampled_data = predictions

heat_data = [[row['latitude'], row['longitude'], row['pm25']] 
             for _, row in sampled_data.iterrows()]
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/map-enhancement`)
3. Commit your changes (`git commit -am 'Add new visualization feature'`)
4. Push to the branch (`git push origin feature/map-enhancement`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**AI-EnviroScan Team**

---

## 🔗 Related Modules

- **Module 1**: Data Collection and Integration
- **Module 2**: Data Cleaning and Preprocessing
- **Module 3**: Feature Engineering
- **Module 4**: Model Training and Source Prediction
- **Module 5**: Geospatial Mapping (This Module)
- **Module 6**: Dashboard Integration

---

## 📚 Resources

- [Folium Documentation](https://python-visualization.github.io/folium/)
- [GeoPandas Documentation](https://geopandas.org/)
- [Leaflet.js Documentation](https://leafletjs.com/)
- [Air Quality Standards](https://www.who.int/airpollution/guidelines/en/)

---

## Geospatial Mapping and Heatmap Visualization  

## Create Sensor Markers Map
<img width="327" height="44" alt="image" src="https://github.com/user-attachments/assets/fc2477cf-ed82-42ff-8318-bc8085ebdbbf" />

## Create Pollution Heatmap
<img width="331" height="105" alt="image" src="https://github.com/user-attachments/assets/62fb859b-dcb1-4681-944c-8a7002003908" />

## Create Risk Zone Map
<img width="340" height="47" alt="image" src="https://github.com/user-attachments/assets/83ff2019-7020-43e5-a078-89ac28d7235e" />

## ALL Maps's and HeatMap Create
<img width="399" height="435" alt="image" src="https://github.com/user-attachments/assets/bf89cef9-dd19-4207-8907-c4b0dae624e8" />
<img width="693" height="433" alt="image" src="https://github.com/user-attachments/assets/87835808-d1c8-4bff-a611-e376a972d03e" />


# Real-Time Dashboard Images

## Dashboard
<img width="1350" height="756" alt="image" src="https://github.com/user-attachments/assets/870299cb-fb7f-4ce3-8ad0-be4f1493f20a" />

## ALL-Zones (6-Zones)
<img width="1351" height="761" alt="image" src="https://github.com/user-attachments/assets/c22bc278-f08b-466a-937a-60d47f621009" />

## Cities (60-Cities)
<img width="1024" height="1536" alt="image" src="https://github.com/user-attachments/assets/3fa0d797-e62a-48c5-b42b-7c63834359b4" />

## Example:- Select West-Zone & City-Nashik REAL TIME DATA
<img width="1339" height="738" alt="image" src="https://github.com/user-attachments/assets/28067302-06b3-45c4-a828-391c513b842e" />


## Current Pollutant Level
<img width="920" height="200" alt="image" src="https://github.com/user-attachments/assets/ed1bdc28-c555-4f81-bda1-050d9fa0d199" />

# Polution Trends Analysis 

## PM2.5
<img width="1313" height="642" alt="image" src="https://github.com/user-attachments/assets/2b0963b8-6f26-4e8d-8b09-57b3cc4a0bca" />

## PM10
<img width="1327" height="670" alt="image" src="https://github.com/user-attachments/assets/8089f208-2343-432d-a4a2-e8f5cb7f7c75" />

## no2
<img width="1328" height="679" alt="image" src="https://github.com/user-attachments/assets/d872164a-94f7-4ed3-9cf4-770fa25116c2" />

## Map - Nashik
<img width="1362" height="681" alt="image" src="https://github.com/user-attachments/assets/d3db607b-b714-4cb1-b4e9-7a4aeab12d67" />
## Real Time Alerts
<img width="1309" height="719" alt="image" src="https://github.com/user-attachments/assets/f56c83e1-3949-4a95-b259-bcb5260d479b" />

## Report's
<img width="1332" height="701" alt="image" src="https://github.com/user-attachments/assets/3d8d98b0-845c-4816-a11a-d31532f142f6" />

## Daily Report Generate(Exel-format)
<img width="1366" height="360" alt="image" src="https://github.com/user-attachments/assets/7f7f4414-0eee-41c4-97db-650d0d9c60c0" />

## Historical Analysis
<img width="548" height="399" alt="image" src="https://github.com/user-attachments/assets/d65feac9-87bb-4bf6-8faf-9dd8fee5167b" />



**Last Updated**: November 2025  
**Version**: 1.0.0
