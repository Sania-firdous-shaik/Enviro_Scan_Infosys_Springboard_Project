# 🌐 AI-EnviroScan: Milestone 1 – Data Collection from APIs and Location Databases

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![OpenAQ](https://img.shields.io/badge/OpenAQ-API-green.svg)](https://openaq.org/)
[![OpenWeatherMap](https://img.shields.io/badge/OpenWeatherMap-API-orange.svg)](https://openweathermap.org/)
[![OSMnx](https://img.shields.io/badge/OSMnx-Geospatial-red.svg)](https://osmnx.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📘 Overview

This module focuses on **gathering real-time environmental data** from multiple public APIs and geospatial sources to build the foundation for the AI-EnviroScan system. It integrates **air quality**, **weather**, and **location-based data** into a structured dataset for further preprocessing, feature engineering, and model training.

The module establishes a robust data pipeline that:
- 🌍 Collects pollution data from multiple Indian cities
- ☁️ Integrates real-time weather information
- 📍 Maps geospatial features and proximity indicators
- 💾 Structures data for ML model training

---

## ⚙️ Data Sources

| Data Type | Source | API / Library | Description |
|-----------|--------|---------------|-------------|
| **Air Quality** | [OpenAQ](https://openaq.org/) | `openaq` API | Pollutant concentrations: PM2.5, PM10, NO₂, CO, SO₂, O₃ |
| **Weather Data** | [OpenWeatherMap](https://openweathermap.org/api) | REST API | Weather metrics: temperature, humidity, wind speed, wind direction |
| **Geospatial Data** | [OpenStreetMap](https://www.openstreetmap.org/) | `OSMnx` | Nearby features: roads, industries, dump sites, agricultural fields |

---

## 🧩 Workflow Summary

### 1️⃣ Setup and Configuration

Install necessary libraries and configure API credentials:

```python
import requests
import pandas as pd
import osmnx as ox
from datetime import datetime
from openaq import OpenAQ

# API Configuration
OPENWEATHER_API_KEY = "YOUR_API_KEY"

# Target cities with coordinates
cities = {
    'Delhi': (28.61, 77.23),
    'Mumbai': (19.07, 72.87),
    'Bangalore': (12.97, 77.59),
    'Pune': (18.52, 73.85),
    'Kolkata': (22.57, 88.36)
}
```

**Required API Keys:**
- 🔑 OpenWeatherMap API key (free tier available)
- 🔑 OpenAQ (no API key required, but rate-limited)

---

### 2️⃣ Collect Air Quality Data (OpenAQ)

Fetch real-time pollutant concentrations for selected Indian cities:

```python
from openaq import OpenAQ

def fetch_air_quality_data(city, parameters=['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']):
    """
    Fetch air quality data from OpenAQ API
    
    Args:
        city: City name
        parameters: List of pollutants to fetch
    
    Returns:
        DataFrame with pollutant measurements
    """
    api = OpenAQ()
    
    status, results = api.measurements(
        city=city,
        parameter=parameters,
        limit=100,
        order_by='datetime',
        sort='desc'
    )
    
    if status == 200:
        df_air = pd.DataFrame(results['results'])
        return df_air
    else:
        print(f"Error fetching data for {city}: Status {status}")
        return None

# Fetch data for all cities
air_quality_data = {}
for city in cities.keys():
    print(f"Fetching air quality data for {city}...")
    air_quality_data[city] = fetch_air_quality_data(city)
```

**Collected Pollutants:**
- **PM2.5** - Fine particulate matter (< 2.5 μm)
- **PM10** - Coarse particulate matter (< 10 μm)
- **NO₂** - Nitrogen dioxide
- **SO₂** - Sulfur dioxide
- **CO** - Carbon monoxide
- **O₃** - Ozone

---

### 3️⃣ Collect Weather Data (OpenWeatherMap)

Fetch meteorological data for each location:

```python
def fetch_weather_data(lat, lon, api_key):
    """
    Fetch weather data from OpenWeatherMap API
    
    Args:
        lat: Latitude
        lon: Longitude
        api_key: OpenWeatherMap API key
    
    Returns:
        Dictionary with weather parameters
    """
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'metric'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'wind_direction': data['wind'].get('deg', 0),
            'weather_condition': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description']
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

# Fetch weather for all cities
weather_data = {}
for city, (lat, lon) in cities.items():
    print(f"Fetching weather data for {city}...")
    weather_data[city] = fetch_weather_data(lat, lon, OPENWEATHER_API_KEY)
```

**Weather Parameters:**
- 🌡️ Temperature (°C)
- 💧 Humidity (%)
- 🌪️ Wind speed (m/s)
- 🧭 Wind direction (degrees)
- ☁️ Weather conditions
- 📊 Atmospheric pressure (hPa)

---

### 4️⃣ Extract Geospatial Features (OpenStreetMap / OSMnx)

Identify nearby physical features that may influence pollution:

```python
def get_nearby_features(lat, lon, radius=1000):
    """
    Extract nearby geospatial features using OSMnx
    
    Args:
        lat: Latitude
        lon: Longitude
        radius: Search radius in meters
    
    Returns:
        DataFrame with nearby features
    """
    try:
        # Get road network
        G = ox.graph_from_point(
            (lat, lon),
            dist=radius,
            network_type='drive'
        )
        
        # Get points of interest
        tags = {
            'landuse': True,
            'highway': True,
            'amenity': True,
            'industrial': True
        }
        
        pois = ox.geometries_from_point(
            (lat, lon),
            tags=tags,
            dist=radius
        )
        
        # Extract relevant features
        features = {
            'road_count': len(G.edges),
            'road_length_km': sum([data['length'] for u, v, data in G.edges(data=True)]) / 1000,
            'industrial_count': len(pois[pois.get('landuse') == 'industrial']) if 'landuse' in pois else 0,
            'residential_count': len(pois[pois.get('landuse') == 'residential']) if 'landuse' in pois else 0,
            'commercial_count': len(pois[pois.get('landuse') == 'commercial']) if 'landuse' in pois else 0,
            'nearby_features': list(pois.get('landuse', []).unique()) if 'landuse' in pois else []
        }
        
        return features
    
    except Exception as e:
        print(f"Error extracting geospatial features: {e}")
        return None

# Extract features for all cities
geospatial_data = {}
for city, (lat, lon) in cities.items():
    print(f"Extracting geospatial features for {city}...")
    geospatial_data[city] = get_nearby_features(lat, lon)
```

**Extracted Attributes:**
- 🛣️ Roads / Highways
- 🏭 Industrial areas
- 🏘️ Residential zones
- 🌾 Farmlands
- 🗑️ Dump yards
- 🏬 Commercial areas

---

### 5️⃣ Combine and Tag All Data

Merge air quality, weather, and geospatial data into a unified dataset:

```python
def create_combined_dataset(cities, air_quality_data, weather_data, geospatial_data):
    """
    Combine all data sources into a single structured dataset
    
    Returns:
        DataFrame with complete environmental data
    """
    records = []
    
    for city, (lat, lon) in cities.items():
        # Get air quality data
        aq_data = air_quality_data.get(city)
        if aq_data is None or aq_data.empty:
            continue
        
        # Get latest measurements for each pollutant
        latest_measurements = {}
        for pollutant in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']:
            pollutant_data = aq_data[aq_data['parameter'] == pollutant]
            if not pollutant_data.empty:
                latest_measurements[pollutant] = pollutant_data.iloc[0]['value']
            else:
                latest_measurements[pollutant] = None
        
        # Get weather data
        weather = weather_data.get(city, {})
        
        # Get geospatial data
        geo = geospatial_data.get(city, {})
        
        # Create record
        record = {
            'city': city,
            'latitude': lat,
            'longitude': lon,
            'timestamp': datetime.now().isoformat(),
            'pm25': latest_measurements.get('pm25'),
            'pm10': latest_measurements.get('pm10'),
            'no2': latest_measurements.get('no2'),
            'so2': latest_measurements.get('so2'),
            'co': latest_measurements.get('co'),
            'o3': latest_measurements.get('o3'),
            'temperature': weather.get('temperature'),
            'humidity': weather.get('humidity'),
            'pressure': weather.get('pressure'),
            'wind_speed': weather.get('wind_speed'),
            'wind_direction': weather.get('wind_direction'),
            'weather_condition': weather.get('weather_condition'),
            'road_count': geo.get('road_count'),
            'road_length_km': geo.get('road_length_km'),
            'industrial_count': geo.get('industrial_count'),
            'residential_count': geo.get('residential_count'),
            'commercial_count': geo.get('commercial_count'),
            'nearby_features': ','.join(geo.get('nearby_features', []))
        }
        
        records.append(record)
    
    df_combined = pd.DataFrame(records)
    return df_combined

# Create combined dataset
df_final = create_combined_dataset(cities, air_quality_data, weather_data, geospatial_data)
print(f"✅ Combined dataset created with {len(df_final)} records")
```

---

### 6️⃣ Store Data for Further Processing

Save the combined dataset in multiple formats:

```python
import os

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Save as CSV
csv_path = 'data/raw_air_quality_data.csv'
df_final.to_csv(csv_path, index=False)
print(f"✅ Data saved to {csv_path}")

# Save as JSON
json_path = 'data/raw_air_quality_data.json'
df_final.to_json(json_path, orient='records', indent=2)
print(f"✅ Data saved to {json_path}")

# Save summary statistics
summary_path = 'exports/data_collection_summary.json'
summary = {
    'collection_date': datetime.now().isoformat(),
    'total_records': len(df_final),
    'cities_covered': df_final['city'].unique().tolist(),
    'pollutants_collected': ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3'],
    'data_completeness': {
        col: (df_final[col].notna().sum() / len(df_final) * 100)
        for col in df_final.columns
    }
}

os.makedirs('exports', exist_ok=True)
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)

print(f"✅ Summary saved to {summary_path}")
```

---

## 📁 Project Structure

```
AI-EnviroScan/
├── AI-EnviroScan/
│   ├── add_all_india_cities_enhanced.py    # Script to enhance city data
│   ├── AI-EnviroScan_Complete_Dashboard.ipynb  # Complete dashboard notebook
│   ├── Final_Dashboard.ipynb               # Final integrated dashboard
│   ├── streamlit_dashboard.py              # Streamlit web application
│   ├── unified_dashboard.py                # Unified dashboard module
│   ├── requirements.txt                    # Python dependencies
│   │
│   ├── data/                               # Pollution datasets
│   │   ├── pollution_data_all_india.csv
│   │   ├── pollution_data_all_india_enhanced.csv
│   │   ├── pollution_data_comprehensive.csv
│   │   └── pollution_data_simple.csv
│   │
│   ├── exports/                            # Generated reports and summaries
│   │   ├── data_collection_summary.json
│   │   ├── model_performance_report.json
│   │   ├── pollution_statistics_report.csv
│   │   ├── prediction_accuracy_report.csv
│   │   ├── sensor_summary_report.csv
│   │   └── map_links_report.csv
│   │
│   ├── maps/                               # Interactive HTML maps
│   │   ├── comprehensive_dashboard_map.html
│   │   ├── pm25_heatmap_map.html
│   │   ├── pm10_heatmap_map.html
│   │   ├── no2_heatmap_map.html
│   │   ├── pollution_source_predictions.html
│   │   ├── risk_zones_map.html
│   │   ├── sensor_markers_map.html
│   │   └── time_animation_map.html
│   │
│   ├── models/                             # Trained ML models
│   │   ├── pollution_source_decision_tree_model.joblib
│   │   ├── pollution_source_random_forest_model.joblib
│   │   ├── pollution_source_xgboost_model.joblib
│   │   ├── pollution_source_model_artifacts.joblib
│   │   └── preprocessing_artifacts.joblib
│   │
│   ├── notebooks/                          # Jupyter notebooks for development
│   │   ├── 01_Data_Collection.ipynb       # This module
│   │   ├── 02_Model_Training.ipynb
│   │   ├── 03_Mapping_Visualization.ipynb
│   │   ├── 04_Dashboard_Preview.ipynb
│   │   └── cache/                          # Notebook cache files
│   │       └── *.json
│   │
│   ├── __pycache__/                        # Python cache files
│   │   └── unified_dashboard.cpython-311.pyc
│   │
│   └── README.md                           # This file
```

### 📂 Directory Descriptions

| Directory | Purpose |
|-----------|---------|
| **data/** | Contains all pollution datasets in various formats (simple, comprehensive, enhanced) |
| **exports/** | Stores generated reports, summaries, and analysis results in JSON/CSV formats |
| **maps/** | Interactive HTML maps for different pollutants and visualizations |
| **models/** | Trained machine learning models (Decision Tree, Random Forest, XGBoost) and preprocessing artifacts |
| **notebooks/** | Jupyter notebooks for development, training, and visualization workflows |
| **__pycache__/** | Python bytecode cache (auto-generated) |

---

## 📊 Example Output

Sample of the collected data:

| city | latitude | longitude | pm25 | pm10 | no2 | so2 | co | o3 | temperature | humidity | wind_speed | nearby_features |
|------|----------|-----------|------|------|-----|-----|----|----|-------------|----------|------------|-----------------|
| Delhi | 28.61 | 77.23 | 135 | 240 | 80 | 25 | 1.1 | 45 | 28.5 | 54 | 2.4 | industrial,residential |
| Pune | 18.52 | 73.85 | 68 | 120 | 42 | 10 | 0.7 | 60 | 30.1 | 58 | 3.8 | residential,highway |
| Mumbai | 19.07 | 72.87 | 89 | 165 | 55 | 18 | 0.9 | 52 | 29.3 | 72 | 3.2 | commercial,residential |
| Bangalore | 12.97 | 77.59 | 52 | 95 | 38 | 8 | 0.6 | 48 | 26.8 | 62 | 2.8 | residential,industrial |

---

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- API keys (OpenWeatherMap)

### Dependencies

Install required packages:

```bash
pip install pandas requests openaq osmnx geopandas
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
pandas>=1.3.0
requests>=2.28.0
openaq>=2.0.0
osmnx>=1.2.0
geopandas>=0.10.0
shapely>=1.8.0
networkx>=2.6.0
```

---

## 🚀 Usage

### Quick Start

```python
# Import libraries
import pandas as pd
from data_collection import fetch_air_quality_data, fetch_weather_data, get_nearby_features

# Define cities
cities = {
    'Delhi': (28.61, 77.23),
    'Mumbai': (19.07, 72.87)
}

# Collect data
for city, (lat, lon) in cities.items():
    aq_data = fetch_air_quality_data(city)
    weather_data = fetch_weather_data(lat, lon, API_KEY)
    geo_data = get_nearby_features(lat, lon)
    
    print(f"✅ Data collected for {city}")
```

### Running the Notebook

```bash
# Start Jupyter
jupyter notebook

# Open notebooks/01_Data_Collection.ipynb
```

---

## 📈 Data Quality Checks

Implement validation to ensure data quality:

```python
def validate_data(df):
    """
    Validate collected data for completeness and accuracy
    """
    checks = {
        'missing_values': df.isnull().sum(),
        'duplicate_records': df.duplicated().sum(),
        'negative_values': (df.select_dtypes(include=['number']) < 0).sum(),
        'outliers': {}
    }
    
    # Check for outliers (values > 3 std deviations)
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        mean = df[col].mean()
        std = df[col].std()
        outliers = df[(df[col] > mean + 3*std) | (df[col] < mean - 3*std)]
        checks['outliers'][col] = len(outliers)
    
    return checks

# Run validation
validation_results = validate_data(df_final)
print("Data Quality Report:")
print(json.dumps(validation_results, indent=2))
```

---

## 🔄 Automation

Set up automated data collection:

```python
import schedule
import time

def collect_data_job():
    """Run data collection workflow"""
    print(f"Starting data collection at {datetime.now()}")
    df = create_combined_dataset(cities, air_quality_data, weather_data, geospatial_data)
    df.to_csv(f'data/pollution_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    print("✅ Data collection completed")

# Schedule data collection every 6 hours
schedule.every(6).hours.do(collect_data_job)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## 🧠 Next Steps

After completing data collection, proceed to:

1. **Module 2**: Data Preprocessing & Cleaning
2. **Module 3**: Feature Engineering
3. **Module 4**: Model Training
4. **Module 5**: Geospatial Visualization
5. **Module 6**: Dashboard Integration

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/data-source`)
3. Commit your changes (`git commit -am 'Add new data source'`)
4. Push to the branch (`git push origin feature/data-source`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---


## 🔗 Related Modules

- **Module 1**: Data Collection (This Module)
- **Module 2**: Data Preprocessing & Cleaning
- **Module 3**: Feature Engineering
- **Module 4**: Model Training and Source Prediction
- **Module 5**: Geospatial Mapping and Visualization
- **Module 6**: Real-Time Dashboard and Alerts

---

## Wether Data Collection
<img width="403" height="378" alt="image" src="https://github.com/user-attachments/assets/e0ba539d-88cf-424d-ad1b-9fc5392c50ad" />

## Data set quality Check
<img width="445" height="503" alt="image" src="https://github.com/user-attachments/assets/a56a5fc2-0a24-4fbd-90e8-33fb3d86a3b9" />

## Basic Visualization
<img width="806" height="471" alt="image" src="https://github.com/user-attachments/assets/7e5ada72-fe52-4c04-a32b-a069dc35337e" />

## Map Visualization
<img width="800" height="249" alt="image" src="https://github.com/user-attachments/assets/ee20424d-dd64-4d85-8260-6f84cdbdae57" />




**Last Updated**: November 2025  
**Version**: 1.0.0  
