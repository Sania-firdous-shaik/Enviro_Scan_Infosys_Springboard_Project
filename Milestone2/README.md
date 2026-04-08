# 🏷️ Spatial Feature Engineering and Pollution Source Labeling


## 🎯 Overview

This module implements an intelligent pollution source labeling system that automatically classifies air pollution sources based on spatial proximity, pollutant signatures, and environmental context. When ground-truth labels are unavailable, it provides synthetic labeled data generation for supervised machine learning model training.

**Key Capabilities:**
- 🎯 Rule-based multi-source classification
- 🧪 Synthetic labeled data generation
- ✅ Domain expert validation framework
- 🔄 Hybrid labeling (rules + ML)
- 📊 Label quality assessment
- 🗺️ Geospatial context integration

---

## 🏭 Pollution Source Categories

### Primary Source Types

| Source Type | Key Pollutants | Typical Locations | Peak Times |
|------------|----------------|-------------------|------------|
| **Vehicular** | NO₂, CO, PM2.5 | Roads, highways, parking | Rush hours (7-9 AM, 5-8 PM) |
| **Industrial** | SO₂, PM10, VOCs | Factories, plants, refineries | Working hours (24/7 for continuous) |
| **Agricultural** | NH₃, PM10, PM2.5 | Farmland, rural areas | Planting/harvest seasons |
| **Biomass Burning** | CO, PM2.5, BC | Residential, rural areas | Evening/night, winter |
| **Construction** | PM10, PM2.5 | Building sites, roads | Daytime (6 AM - 6 PM) |
| **Natural** | Dust, pollen, O₃ | Open areas, forests | Seasonal, wind-dependent |

### Pollutant Signature Profiles

```python
POLLUTANT_SIGNATURES = {
    'Vehicular': {
        'dominant': ['NO2', 'CO'],
        'secondary': ['PM2.5', 'BC'],
        'ratios': {'NO2/PM2.5': (0.5, 2.0), 'CO/NO2': (0.3, 1.5)}
    },
    'Industrial': {
        'dominant': ['SO2', 'PM10'],
        'secondary': ['VOCs', 'Heavy_metals'],
        'ratios': {'SO2/PM10': (0.1, 0.8), 'PM10/PM2.5': (1.5, 3.0)}
    },
    'Agricultural': {
        'dominant': ['NH3', 'PM10'],
        'secondary': ['PM2.5'],
        'ratios': {'PM10/PM2.5': (2.0, 5.0), 'NH3/PM10': (0.1, 0.5)}
    },
    'Biomass_Burning': {
        'dominant': ['CO', 'PM2.5', 'BC'],
        'secondary': ['VOCs', 'PAHs'],
        'ratios': {'CO/PM2.5': (1.0, 3.0), 'BC/PM2.5': (0.05, 0.15)}
    },
    'Construction': {
        'dominant': ['PM10', 'PM2.5'],
        'secondary': ['Dust'],
        'ratios': {'PM10/PM2.5': (2.0, 4.0)}
    },
    'Natural': {
        'dominant': ['O3', 'Dust', 'Pollen'],
        'secondary': ['PM10'],
        'ratios': {'O3/NO2': (1.5, 5.0)}
    }
}
```

---

## 🔬 Labeling Methodology

### Three-Tier Labeling Approach

```
┌─────────────────────────────────────────────────────────┐
│  Tier 1: Spatial Proximity Analysis                    │
│  → Distance to roads, factories, farms, etc.           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Tier 2: Pollutant Signature Matching                  │
│  → Compare measured ratios with known signatures       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Tier 3: Temporal Context Analysis                     │
│  → Time of day, season, weather conditions             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
           [Final Label Assignment]
```

---

## 📦 Installation

```bash
# Clone repository
git clone <repository-url>
cd module-3-source-labeling

# Install dependencies
pip install -r requirements.txt

# Install geospatial libraries
pip install geopandas shapely rtree

# Optional: Install validation tools
pip install scikit-learn imbalanced-learn
```

### Dependencies

```txt
pandas>=1.3.0
numpy>=1.21.0
geopandas>=0.10.0
shapely>=1.8.0
scikit-learn>=1.0.0
pyyaml>=5.4.0
scipy>=1.7.0
matplotlib>=3.4.0
seaborn>=0.11.0
```

---

## 🎯 Rule-Based Labeling System

### 1. Vehicular Source Detection

**Rules:**
- Distance to road < 100m
- High NO₂ levels (>40 μg/m³)
- NO₂/PM2.5 ratio: 0.5-2.0
- Peak during rush hours

```python
from source_labeling import VehicularLabeler

vehicular_labeler = VehicularLabeler(
    distance_threshold=100,  # meters
    no2_threshold=40,        # μg/m³
    ratio_bounds=(0.5, 2.0),
    peak_hours=[(7, 9), (17, 20)]
)

# Apply labeling
labels = vehicular_labeler.predict(df)

# Example rule implementation
def is_vehicular(row):
    """Determine if pollution is from vehicular sources."""
    conditions = [
        row['distance_to_road'] < 100,
        row['NO2'] > 40,
        0.5 < row['NO2'] / max(row['PM2.5'], 1) < 2.0,
        row['hour'] in [7, 8, 9, 17, 18, 19, 20]
    ]
    
    confidence = sum(conditions) / len(conditions)
    return confidence > 0.6  # 60% confidence threshold
```

### 2. Industrial Source Detection

**Rules:**
- Distance to industrial zone < 500m
- High SO₂ (>20 μg/m³) or PM10 (>100 μg/m³)
- SO₂/PM10 ratio: 0.1-0.8
- Consistent throughout work hours

```python
from source_labeling import IndustrialLabeler

industrial_labeler = IndustrialLabeler(
    distance_threshold=500,
    so2_threshold=20,
    pm10_threshold=100,
    ratio_bounds=(0.1, 0.8),
    operating_hours=(0, 24)  # 24/7 for continuous processes
)

def is_industrial(row):
    """Determine if pollution is from industrial sources."""
    
    # Primary conditions
    near_industry = row['distance_to_industrial'] < 500
    high_so2 = row['SO2'] > 20
    high_pm10 = row['PM10'] > 100
    
    # Signature matching
    so2_pm10_ratio = row['SO2'] / max(row['PM10'], 1)
    correct_ratio = 0.1 < so2_pm10_ratio < 0.8
    
    # Temporal consistency (industrial sources are steady)
    temporal_consistency = row['pollutant_variance'] < 0.3
    
    # Weighted scoring
    score = (
        near_industry * 0.4 +
        (high_so2 or high_pm10) * 0.3 +
        correct_ratio * 0.2 +
        temporal_consistency * 0.1
    )
    
    return score > 0.5
```

### 3. Agricultural Source Detection

**Rules:**
- Distance to farmland < 1000m
- High PM10 (>80 μg/m³) with PM10/PM2.5 ratio > 2.0
- High NH₃ if available
- Dry season + wind conditions

```python
from source_labeling import AgriculturalLabeler

agricultural_labeler = AgriculturalLabeler(
    distance_threshold=1000,
    pm10_threshold=80,
    pm_ratio_threshold=2.0,
    seasons=['spring', 'fall'],  # Planting/harvest
    wind_speed_min=3.0  # m/s for dust transport
)

def is_agricultural(row):
    """Determine if pollution is from agricultural sources."""
    
    # Location check
    near_farmland = row['distance_to_farmland'] < 1000
    
    # Dust signature (coarse particles)
    high_pm10 = row['PM10'] > 80
    pm_ratio = row['PM10'] / max(row['PM2.5'], 1)
    coarse_dominant = pm_ratio > 2.0
    
    # Seasonal patterns
    is_harvest_season = row['season'] in ['spring', 'fall']
    
    # Wind-driven transport
    windy_conditions = row['wind_speed'] > 3.0
    dry_conditions = row['humidity'] < 50
    
    # Combine conditions
    conditions = [
        near_farmland,
        high_pm10 and coarse_dominant,
        is_harvest_season,
        windy_conditions and dry_conditions
    ]
    
    return sum(conditions) >= 3  # Need at least 3/4 conditions
```

### 4. Biomass Burning Detection

**Rules:**
- High CO (>3 ppm) and PM2.5 (>75 μg/m³)
- CO/PM2.5 ratio: 1.0-3.0
- Evening/night hours or winter season
- Residential areas or rural regions

```python
from source_labeling import BiomassBurningLabeler

biomass_labeler = BiomassBurningLabeler(
    co_threshold=3.0,        # ppm
    pm25_threshold=75,       # μg/m³
    ratio_bounds=(1.0, 3.0),
    peak_hours=(18, 23),     # Evening cooking/heating
    peak_seasons=['winter']
)

def is_biomass_burning(row):
    """Determine if pollution is from biomass burning."""
    
    # Signature pollutants
    high_co = row['CO'] > 3.0
    high_pm25 = row['PM2.5'] > 75
    
    # Characteristic ratio
    co_pm25_ratio = row['CO'] / max(row['PM2.5'], 1)
    correct_ratio = 1.0 < co_pm25_ratio < 3.0
    
    # Temporal patterns
    evening_peak = 18 <= row['hour'] <= 23
    winter_season = row['season'] == 'winter'
    
    # Black carbon indicator (if available)
    high_bc = row.get('BC', 0) / max(row['PM2.5'], 1) > 0.05
    
    # Decision logic
    has_signature = high_co and high_pm25 and correct_ratio
    has_timing = evening_peak or winter_season
    
    return has_signature and has_timing
```

### 5. Construction Source Detection

**Rules:**
- Distance to construction site < 200m
- Very high PM10 (>150 μg/m³)
- PM10/PM2.5 ratio: 2.0-4.0
- Daytime hours (6 AM - 6 PM)

```python
from source_labeling import ConstructionLabeler

construction_labeler = ConstructionLabeler(
    distance_threshold=200,
    pm10_threshold=150,
    ratio_bounds=(2.0, 4.0),
    working_hours=(6, 18)
)

def is_construction(row):
    """Determine if pollution is from construction activities."""
    
    # Proximity check
    near_construction = row['distance_to_construction'] < 200
    
    # Dust characteristics (very coarse)
    very_high_pm10 = row['PM10'] > 150
    pm_ratio = row['PM10'] / max(row['PM2.5'], 1)
    very_coarse = 2.0 < pm_ratio < 4.0
    
    # Daytime activity only
    is_working_hours = 6 <= row['hour'] <= 18
    is_weekday = row['day_of_week'] < 5
    
    # Sudden spikes (not continuous)
    is_spike = row['pm10_1h_change'] > 50
    
    return (near_construction and 
            very_high_pm10 and 
            very_coarse and 
            is_working_hours and 
            is_weekday)
```

### 6. Natural Source Detection

**Rules:**
- High O₃ or pollen during appropriate seasons
- Low anthropogenic markers (NO₂, SO₂)
- Open areas, forests, or deserts
- Weather-dependent (wind, temperature)

```python
from source_labeling import NaturalLabeler

natural_labeler = NaturalLabeler(
    o3_threshold=100,  # μg/m³
    anthropogenic_threshold=20,  # Low NO₂/SO₂
    wind_speed_min=5.0  # For dust transport
)

def is_natural(row):
    """Determine if pollution is from natural sources."""
    
    # Low anthropogenic markers
    low_no2 = row['NO2'] < 20
    low_so2 = row['SO2'] < 10
    
    # Natural source indicators
    high_o3 = row.get('O3', 0) > 100  # Photochemical
    high_dust = row['PM10'] > 100 and row['humidity'] < 30
    
    # Location context
    in_natural_area = (
        row['distance_to_forest'] < 500 or
        row['distance_to_desert'] < 2000
    )
    
    # Meteorological conditions
    strong_wind = row['wind_speed'] > 5.0
    dry_conditions = row['humidity'] < 40
    
    # Natural dust event
    dust_event = high_dust and strong_wind and dry_conditions
    
    # Photochemical ozone
    ozone_event = high_o3 and row['temperature'] > 30 and row['hour'] in range(12, 17)
    
    return (low_no2 and low_so2 and 
            in_natural_area and 
            (dust_event or ozone_event))
```

---

## 🎲 Simulation Engine

### Synthetic Labeled Data Generation

When ground-truth labels are unavailable, simulate realistic labeled datasets:

```python
from source_labeling import SyntheticDataGenerator

# Initialize generator
generator = SyntheticDataGenerator(
    n_samples=10000,
    source_distribution={
        'Vehicular': 0.35,
        'Industrial': 0.25,
        'Agricultural': 0.15,
        'Biomass_Burning': 0.15,
        'Construction': 0.05,
        'Natural': 0.05
    },
    noise_level=0.15  # 15% noise in features
)

# Generate synthetic dataset
synthetic_df = generator.generate(
    base_features=['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3'],
    spatial_features=['distance_to_road', 'distance_to_industrial'],
    temporal_features=['hour', 'day_of_week', 'season']
)

# Add realistic noise and variability
synthetic_df = generator.add_noise(synthetic_df, method='gaussian')
synthetic_df = generator.add_outliers(synthetic_df, fraction=0.02)

# Save synthetic data
synthetic_df.to_csv('data/labeled/synthetic_training_data.csv', index=False)
```

### Simulation Parameters

```python
SIMULATION_CONFIG = {
    'Vehicular': {
        'base_levels': {
            'NO2': (40, 120),   # μg/m³
            'PM2.5': (35, 100),
            'CO': (1.5, 5.0)    # ppm
        },
        'temporal_pattern': 'rush_hour',  # Peak at 7-9, 17-20
        'spatial_decay': 'exponential',   # Distance-based decay
        'variability': 0.25  # 25% random variation
    },
    'Industrial': {
        'base_levels': {
            'SO2': (20, 80),
            'PM10': (100, 300),
            'VOC': (10, 50)
        },
        'temporal_pattern': 'steady',     # Consistent 24/7
        'spatial_decay': 'gaussian',      # Plume dispersion
        'variability': 0.15
    },
    'Agricultural': {
        'base_levels': {
            'PM10': (80, 200),
            'NH3': (20, 100),
            'PM2.5': (30, 80)
        },
        'temporal_pattern': 'seasonal',   # Spring/fall peaks
        'spatial_decay': 'linear',
        'variability': 0.40  # High variability
    }
}
```

### Advanced Simulation Techniques

```python
# 1. Multi-source mixing (realistic scenarios)
mixed_samples = generator.generate_mixed_sources(
    primary_sources=['Vehicular', 'Industrial'],
    mixing_ratios=[(0.7, 0.3), (0.5, 0.5), (0.8, 0.2)],
    n_samples=1000
)

# 2. Meteorological influence
meteorology_sim = generator.add_meteorological_effects(
    synthetic_df,
    wind_dispersion=True,
    temperature_photochemistry=True,
    humidity_deposition=True
)

# 3. Diurnal and seasonal variations
temporal_sim = generator.add_temporal_patterns(
    synthetic_df,
    diurnal_cycles=True,
    weekly_patterns=True,
    seasonal_trends=True
)

# 4. Spatial heterogeneity
spatial_sim = generator.add_spatial_variations(
    synthetic_df,
    urban_gradient=True,
    point_sources=[(lat1, lon1), (lat2, lon2)],
    dispersion_model='gaussian_plume'
)
```

---

## ✅ Validation Framework

### 1. Domain Expert Validation

```python
from source_labeling import DomainExpertValidator

validator = DomainExpertValidator()

# Load reference knowledge base
validator.load_expert_rules('config/expert_rules.yaml')

# Validate labeling logic
validation_results = validator.validate(
    labeled_data=df_labeled,
    checks=[
        'pollutant_ratios',
        'spatial_consistency',
        'temporal_patterns',
        'physical_plausibility'
    ]
)

# Generate validation report
print(f"Validation Score: {validation_results['overall_score']:.2%}")
print(f"Failed Checks: {validation_results['failed_checks']}")

# Example expert rules
EXPERT_VALIDATION_RULES = {
    'Vehicular': {
        'must_have': ['NO2 > 30', 'distance_to_road < 200'],
        'should_have': ['CO > 1.0', 'rush_hour_peak'],
        'cannot_have': ['SO2 > 50', 'distance_to_road > 500']
    },
    'Industrial': {
        'must_have': ['SO2 > 15 OR PM10 > 80'],
        'should_have': ['distance_to_industrial < 1000'],
        'cannot_have': ['only_rush_hour_pattern']
    }
}
```

### 2. Cross-Validation with Reference Data

```python
from source_labeling import ReferenceDataValidator

# Compare with external datasets
ref_validator = ReferenceDataValidator()

# Load reference data (if available)
ref_data = ref_validator.load_reference(
    sources=[
        'EPA_emissions_inventory',
        'satellite_hotspots',
        'traffic_counts',
        'industrial_registry'
    ]
)

# Cross-validate labels
agreement_score = ref_validator.calculate_agreement(
    predicted_labels=df_labeled['source'],
    reference_locations=ref_data['locations'],
    tolerance=500  # meters
)

print(f"Agreement with Reference Data: {agreement_score:.2%}")
```

### 3. Statistical Consistency Checks

```python
from source_labeling import StatisticalValidator

stat_validator = StatisticalValidator()

# Check label distribution
distribution_check = stat_validator.check_distribution(
    labels=df_labeled['source'],
    expected_distribution={
        'Vehicular': (0.30, 0.40),
        'Industrial': (0.20, 0.30),
        'Agricultural': (0.10, 0.20),
        'Other': (0.10, 0.20)
    }
)

# Check feature-label correlations
correlation_check = stat_validator.check_correlations(
    data=df_labeled,
    expected_correlations={
        ('Vehicular', 'NO2'): (0.6, 0.9),
        ('Industrial', 'SO2'): (0.5, 0.8),
        ('Agricultural', 'NH3'): (0.4, 0.7)
    }
)

# Physical plausibility checks
plausibility_check = stat_validator.check_plausibility(
    data=df_labeled,
    rules=[
        'Vehicular => distance_to_road < 500',
        'Industrial => SO2 > 10 OR PM10 > 50',
        'Agricultural => rural_area == True'
    ]
)
```

---

## 💻 Usage Examples

### Basic Labeling Pipeline

```python
from source_labeling import MultiSourceLabeler

# Initialize multi-source labeler
labeler = MultiSourceLabeler(
    config_path='config/labeling_rules.yaml',
    confidence_threshold=0.6
)

# Load cleaned feature data (from Module 2)
df = pd.read_csv('data/processed/final_feature_dataset.csv')

# Apply rule-based labeling
df_labeled = labeler.fit_predict(
    data=df,
    method='hierarchical',  # Try rules in priority order
    handle_ambiguous='most_confident'
)

# View results
print(df_labeled['source'].value_counts())
print(f"\nLabeling Confidence: {df_labeled['source_confidence'].mean():.2%}")

# Save labeled dataset
df_labeled.to_csv('data/labeled/labeled_dataset.csv', index=False)
```

### Advanced: Ensemble Labeling

```python
from source_labeling import EnsembleLabeler

# Create ensemble of labelers
ensemble = EnsembleLabeler(
    labelers=[
        ('rule_based', RuleBasedLabeler()),
        ('ml_based', MLBasedLabeler()),
        ('hybrid', HybridLabeler())
    ],
    voting='weighted',  # Options: 'majority', 'weighted', 'unanimous'
    weights=[0.4, 0.3, 0.3]
)

# Train ML-based component (if reference labels available)
if reference_labels_available:
    ensemble.train(X_train, y_train)

# Apply ensemble labeling
df_labeled = ensemble.predict(df)

# Get label probabilities for all sources
label_probs = ensemble.predict_proba(df)
```

### Handling Ambiguous Cases

```python
from source_labeling import AmbiguityHandler

handler = AmbiguityHandler(threshold=0.6)

# Identify ambiguous samples (low confidence)
ambiguous_mask = df_labeled['source_confidence'] < 0.6

# Option 1: Multi-label assignment
df_multi_label = handler.assign_multi_labels(
    df_labeled[ambiguous_mask],
    min_confidence=0.3,
    max_labels=2
)

# Option 2: Create 'Mixed' category
df_labeled.loc[ambiguous_mask, 'source'] = 'Mixed'

# Option 3: Request manual review
ambiguous_samples = df_labeled[ambiguous_mask]
ambiguous_samples.to_csv('data/review/ambiguous_samples.csv', index=False)
```

### Complete Pipeline Example

```python
import pandas as pd
from source_labeling import (
    MultiSourceLabeler,
    SyntheticDataGenerator,
    DomainExpertValidator,
    LabelQualityAssessor
)

# Step 1: Load feature data
df = pd.read_csv('data/processed/final_feature_dataset.csv')

# Step 2: Apply rule-based labeling
labeler = MultiSourceLabeler()
df_labeled = labeler.fit_predict(df)

# Step 3: Validate labels
validator = DomainExpertValidator()
validation_results = validator.validate(df_labeled)

if validation_results['overall_score'] < 0.7:
    print("Warning: Low validation score. Review labeling rules.")

# Step 4: Generate additional synthetic data (if needed)
generator = SyntheticDataGenerator()
synthetic_df = generator.generate(
    n_samples=5000,
    based_on=df_labeled,  # Match distribution
    augment_minority=True  # Oversample rare classes
)

# Step 5: Combine real and synthetic data
df_final = pd.concat([df_labeled, synthetic_df], ignore_index=True)

# Step 6: Quality assessment
assessor = LabelQualityAssessor()
quality_report = assessor.assess(df_final)
print(quality_report)

# Step 7: Export final labeled dataset
df_final.to_csv('data/labeled/final_labeled_dataset.csv', index=False)

# Step 8: Create train/validation/test splits
from sklearn.model_selection import train_test_split

train_df, temp_df = train_test_split(df_final, test_size=0.3, stratify=df_final['source'])
val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['source'])

# Save splits
train_df.to_csv('data/labeled/train.csv', index=False)
val_df.to_csv('data/labeled/validation.csv', index=False)
test_df.to_csv('data/labeled/test.csv', index=False)

print(f"Training samples: {len(train_df)}")
print(f"Validation samples: {len(val_df)}")
print(f"Test samples: {len(test_df)}")
```

---

## 🚀 Advanced Techniques

### 1. Active Learning for Label Refinement

```python
from source_labeling import ActiveLearner

# Initialize active learner
active_learner = ActiveLearner(
    base_model='random_forest',
    query_strategy='uncertainty_sampling'
)

# Identify samples for manual labeling
uncertain_samples = active_learner.query(
    X=df[features],
    n_samples=100,  # Request 100 labels
    strategy='most_uncertain'
)

# Incorporate manual labels
manual_labels = get_expert_labels(uncertain_samples)
active_learner.update(uncertain_samples, manual_labels)

# Retrain with refined labels
df_refined = active_learner.predict(df)
```

### 2. Semi-Supervised Label Propagation

```python
from source_labeling import SemiSupervisedLabeler

# Use small set of confirmed labels to propagate
ssl_labeler = SemiSupervisedLabeler(method='label_propagation')

# Start with high-confidence labels as seed
seed_labels = df_labeled[df_labeled['source_confidence'] > 0.8]

# Propagate to unlabeled/low-confidence samples
df_propagated = ssl_labeler.fit_predict(
    labeled_data=seed_labels,
    unlabeled_data=df_labeled[df_labeled['source_confidence'] <= 0.8],
    n_iterations=10
)
```

### 3. Temporal Consistency Enforcement

```python
from source_labeling import TemporalConsistencyEnforcer

# Enforce temporal smoothness
enforcer = TemporalConsistencyEnforcer(
    window_size='1H',  # 1-hour windows
    min_consistency=0.7
)

# Smooth labels over time for same location
df_smooth = enforcer.enforce_consistency(
    data=df_labeled,
    group_by='location_id',
    time_col='timestamp'
)
```

---

## 📊 Performance Metrics

### Label Quality Metrics

```python
from source_labeling import LabelQualityMetrics

metrics = LabelQualityMetrics()

# Calculate comprehensive metrics
quality_scores = metrics.calculate(
    data=df_labeled,
    metrics=[
        'confidence_distribution',
        'spatial_consistency',
        'temporal_consistency',
        'class_balance',
        'feature_discriminability'
    ]
)

# Example output:
# {
#     'average_confidence': 0.75,
#     'spatial_consistency': 0.82,
#     'temporal_consistency': 0.78,
#     'class_balance': {
#         'Vehicular': 0.35,
#         'Industrial': 0.28,
#         'Agricultural': 0.15,
#         ...
#     },
#     'feature_discriminability': 0.71
# }
```

### Validation Against Reference Data

```python
from sklearn.metrics import classification_report, confusion_matrix

# If reference labels available
if has_reference_labels:
    y_true = reference_df['source']
    y_pred = df_labeled['source']
    
    # Classification metrics
    print(classification_report(y_true, y_pred))
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    plot_confusion_matrix(cm, labels=source_categories)
    
    # Source-specific accuracy
    for source in source_categories:
        mask = y_true == source
        accuracy = (y_true[mask] == y_pred[mask]).mean()
        print(f"{source}: {accuracy:.2%}")
```


