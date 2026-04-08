# 🧠 Machine Learning Model Training and Performance Evaluation

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0%2B-orange.svg)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-Latest-red.svg)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📘 Overview

This module forms the **core intelligence** of the AI-EnviroScan system, focusing on training machine learning models to predict the **source of air pollution** based on pollutant concentrations, weather conditions, and geographical proximity features.

The system enables accurate identification of pollution sources including:
- 🏭 **Industrial emissions**
- 🚗 **Traffic-related pollution**
- 🏘️ **Residential sources**
- 🌾 **Agricultural activities**
- 🌿 **Natural causes**

---

## 🎯 Key Features

- **Multi-Model Training**: Implements Random Forest, XGBoost, and Decision Tree classifiers
- **Hyperparameter Optimization**: Uses GridSearchCV for optimal model performance
- **Comprehensive Evaluation**: Multiple metrics including accuracy, precision, recall, and F1-score
- **Production-Ready Export**: Saves trained models for dashboard integration
- **Feature Engineering**: Incorporates pollutant, meteorological, and geospatial data

---

## ⚙️ Workflow

### 1️⃣ Data Preparation

The module begins by preparing the dataset for training:

```python
from sklearn.model_selection import train_test_split

# Extract features and target variable
X = df[[
    'pm25', 'pm10', 'no2', 'so2', 'co', 'o3',
    'temperature', 'humidity', 'wind_speed', 'proximity_index'
]]
y = df['pollution_source']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

**Input Features:**
- **Pollutant Concentrations**: PM2.5, PM10, NO₂, SO₂, CO, O₃
- **Meteorological Data**: Temperature, humidity, wind speed, pressure
- **Geospatial Indicators**: Proximity index to known pollution sources

**Target Variable**: `pollution_source` (categorical)

---

### 2️⃣ Model Training

Three classification models are trained and compared:

```python
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.tree import DecisionTreeClassifier

# Initialize models
rf_model = RandomForestClassifier(random_state=42)
xgb_model = XGBClassifier(random_state=42)
dt_model = DecisionTreeClassifier(random_state=42)

# Train models
rf_model.fit(X_train, y_train)
xgb_model.fit(X_train, y_train)
dt_model.fit(X_train, y_train)
```

| Model | Description |
|-------|-------------|
| 🌲 **Random Forest** | Ensemble method using multiple decision trees |
| ⚡ **XGBoost** | Gradient boosting framework for high performance |
| 🌳 **Decision Tree** | Single tree-based classifier for baseline comparison |

---

### 3️⃣ Hyperparameter Tuning

Optimize model parameters for improved accuracy:

```python
from sklearn.model_selection import GridSearchCV

# Define parameter grid
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [5, 10, 15],
    'min_samples_split': [2, 5, 10]
}

# Perform grid search
grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=3,
    scoring='f1_macro'
)
grid_search.fit(X_train, y_train)

# Get best model
best_model = grid_search.best_estimator_
```

**Optimization Strategy:**
- Cross-validation with 3 folds
- F1-macro scoring for balanced class performance
- Systematic parameter space exploration

---

### 4️⃣ Model Evaluation

Comprehensive evaluation using multiple metrics:

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, confusion_matrix, classification_report
)

# Generate predictions
y_pred = best_model.predict(X_test)

# Calculate metrics
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred, average='macro'))
print("Recall:", recall_score(y_test, y_pred, average='macro'))
print("F1 Score:", f1_score(y_test, y_pred, average='macro'))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
```

#### 📊 Evaluation Metrics

| Metric | Description |
|--------|-------------|
| ✅ **Accuracy** | Overall correct predictions |
| 🎯 **Precision** | Reliability of positive predictions |
| 🔁 **Recall** | Ability to capture all relevant sources |
| 🧩 **F1-Score** | Harmonic mean of precision and recall |
| 📊 **Confusion Matrix** | Class-wise prediction distribution |

---

### 5️⃣ Model Export

Export the trained model for production use:

```python
import joblib

# Save model
joblib.dump(best_model, 'pollution_source_model.joblib')
print("✅ Model saved successfully!")
```

The exported model can be loaded in downstream applications:

```python
import joblib

# Load model
model = joblib.load('pollution_source_model.joblib')

# Make predictions
prediction = model.predict(new_data)
```

---

## 📈 Results

**Best Performing Model**: Random Forest / XGBoost (after hyperparameter tuning)

- ✅ High accuracy across all pollution source categories
- 🎯 Balanced precision and recall metrics
- 📊 Strong performance on multi-class classification
- 💾 Model file: `pollution_source_model.joblib`

---

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Dependencies

Install required packages:

```bash
pip install pandas numpy scikit-learn xgboost joblib
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=1.0.0
xgboost>=1.5.0
joblib>=1.0.0
```

---

## 🚀 Usage

### Basic Training Pipeline

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load data
df = pd.read_csv('cleaned_pollution_data.csv')

# Prepare features
X = df[['pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 
        'temperature', 'humidity', 'wind_speed', 'proximity_index']]
y = df['pollution_source']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, 'pollution_source_model.joblib')
```

### Loading and Using the Model

```python
import joblib
import pandas as pd

# Load trained model
model = joblib.load('pollution_source_model.joblib')

# Prepare new data
new_data = pd.DataFrame({
    'pm25': [45.2],
    'pm10': [78.5],
    'no2': [32.1],
    'so2': [12.4],
    'co': [1.2],
    'o3': [28.6],
    'temperature': [25.3],
    'humidity': [65.0],
    'wind_speed': [4.5],
    'proximity_index': [0.7]
})

# Make prediction
prediction = model.predict(new_data)
print(f"Predicted pollution source: {prediction[0]}")
```

---

## 🧩 Integration with Other Modules

This module integrates with the AI-EnviroScan ecosystem:

### Module 5: Dashboard Integration
- Load the trained model for real-time predictions
- Visualize predicted sources on geospatial maps
- Support decision-making for environmental authorities

```python
import joblib
import streamlit as st

# Load model in dashboard
@st.cache_resource
def load_model():
    return joblib.load('pollution_source_model.joblib')

model = load_model()

# Use for real-time predictions
prediction = model.predict(sensor_data)
```

---

## 📊 Model Performance

Expected performance metrics on test data:

| Metric | Value |
|--------|-------|
| Accuracy | ~85-92% |
| Macro Precision | ~83-90% |
| Macro Recall | ~82-89% |
| Macro F1-Score | ~82-89% |

*Note: Actual performance depends on data quality and distribution*

---

## 🔍 Feature Importance

The model identifies key features contributing to predictions:

```python
import matplotlib.pyplot as plt
import numpy as np

# Get feature importance
importances = best_model.feature_importances_
features = X.columns

# Sort and plot
indices = np.argsort(importances)[::-1]
plt.figure(figsize=(10, 6))
plt.bar(range(len(importances)), importances[indices])
plt.xticks(range(len(importances)), features[indices], rotation=45)
plt.title('Feature Importance for Pollution Source Prediction')
plt.tight_layout()
plt.show()
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**AI-EnviroScan Team**

---

## 🙏 Acknowledgments

- Scikit-learn community for robust ML tools
- XGBoost developers for efficient gradient boosting
- Open-source environmental data providers

---

## 🔗 Related Modules

- **Module 1**: Data Collection and Integration
- **Module 2**: Data Cleaning and Preprocessing
- **Module 3**: Feature Engineering
- **Module 4**: Model Training (This Module)
- **Module 5**: Dashboard Integration

---


## Hyperparameter Tuning
<img width="647" height="215" alt="image" src="https://github.com/user-attachments/assets/740dea8c-3db1-49bf-8d6d-9be70ed731fb" />

## Model Training and Evaluation
<img width="266" height="270" alt="image" src="https://github.com/user-attachments/assets/0fc1a412-a796-4957-bafa-3ad887106b36" />

## Model Performance Comparison
<img width="434" height="128" alt="image" src="https://github.com/user-attachments/assets/e0424675-5f70-4db5-82e0-9f6c4ce85103" />

## Model Perfomance Comparison 
<img width="917" height="607" alt="image" src="https://github.com/user-attachments/assets/3b126ce5-1577-43f4-9212-79a10b6c9484" />

## Confusion Matrix
<img width="1360" height="406" alt="image" src="https://github.com/user-attachments/assets/eb271704-2d50-4f1c-8127-69a3cbfe2a2b" />

## Analyzing Feature Importance
<img width="1360" height="598" alt="image" src="https://github.com/user-attachments/assets/778d75be-5c54-4b79-8b40-aabb542ae0da" />

## Deatailed Report
<img width="435" height="515" alt="image" src="https://github.com/user-attachments/assets/9e918778-7864-4d26-b3b6-538fed804702" />

## 
**Last Updated**: November 2025  
**Version**: 1.0.0
