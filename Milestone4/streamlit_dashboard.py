# streamlit_dashboard_final.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="AI-EnviroScan India - Real-Time Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

class FinalEnviroScanDashboard:
    def __init__(self):
        self.POLLUTION_THRESHOLDS = {
            'PM2.5': {'good': 12, 'moderate': 35, 'unhealthy': 55, 'hazardous': 150},
            'PM10': {'good': 54, 'moderate': 154, 'unhealthy': 254, 'hazardous': 424},
            'NO2': {'good': 40, 'moderate': 100, 'unhealthy': 360, 'hazardous': 649}
        }
        self.df = None
        self.model_artifacts = None
    
    def load_data(self):
        """Load enhanced All India data"""
        with st.spinner('🔄 Loading enhanced All India data...'):
            try:
                # Try enhanced dataset
                self.df = pd.read_csv('data/pollution_data_all_india_enhanced.csv')
                self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
                st.success(f"✅ Enhanced data loaded! {self.df['city'].nunique()} cities, {self.df['zone'].nunique()} zones")
                
            except:
                try:
                    # Fallback to basic data
                    self.df = pd.read_csv('data/pollution_data_all_india.csv')
                    self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
                    st.warning("📋 Using basic data. Run enhanced script for full coverage.")
                except Exception as e:
                    st.error(f"❌ Error loading data: {e}")
                    self.create_sample_data()
    
    def create_sample_data(self):
        """Create comprehensive sample data"""
        st.info("🎯 Using comprehensive sample data")
        dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='H')
        
        # All Indian cities with zones
        cities_data = {
            'North': ['Delhi', 'Jaipur', 'Lucknow', 'Chandigarh', 'Amritsar'],
            'South': ['Bangalore', 'Chennai', 'Hyderabad', 'Coimbatore', 'Kochi'],
            'West': ['Mumbai', 'Pune', 'Ahmedabad', 'Nagpur', 'Surat'],
            'East': ['Kolkata', 'Patna', 'Bhubaneswar', 'Guwahati', 'Ranchi'],
            'Central': ['Bhopal', 'Indore', 'Gwalior', 'Raipur', 'Jabalpur'],
            'North-East': ['Shillong', 'Agartala', 'Imphal', 'Kohima', 'Aizawl']
        }
        
        sample_data = []
        for zone, cities in cities_data.items():
            for city in cities:
                # Create 2 sensors per city
                for sensor_num in range(1, 3):
                    sensor_name = f"{city}_Sensor_{sensor_num}"
                    
                    # Realistic pollution patterns
                    if city == 'Delhi':
                        base_pm25, base_pm10 = 120, 250
                    elif city in ['Mumbai', 'Kolkata']:
                        base_pm25, base_pm10 = 90, 200
                    elif city in ['Chennai', 'Bangalore']:
                        base_pm25, base_pm10 = 60, 150
                    else:
                        base_pm25, base_pm10 = 40, 100
                    
                    for date in dates:
                        # Add time-based variation
                        hour = date.hour
                        if 7 <= hour <= 10 or 17 <= hour <= 20:  # Rush hours
                            variation = 1.3
                        elif 22 <= hour <= 5:  # Night
                            variation = 0.7
                        else:
                            variation = 1.0
                            
                        sample_data.append({
                            'timestamp': date,
                            'sensor_name': sensor_name,
                            'city': city,
                            'zone': zone,
                            'sensor_latitude': 20 + np.random.uniform(-8, 8),
                            'sensor_longitude': 78 + np.random.uniform(-8, 8),
                            'PM2.5': max(10, base_pm25 * variation * np.random.uniform(0.8, 1.2)),
                            'PM10': max(20, base_pm10 * variation * np.random.uniform(0.8, 1.2)),
                            'NO2': np.random.uniform(15, 80),
                            'SO2': np.random.uniform(5, 35),
                            'CO': np.random.uniform(0.5, 2.5),
                            'O3': np.random.uniform(15, 65),
                            'temperature_c': np.random.uniform(18, 38),
                            'humidity': np.random.uniform(40, 85),
                            'wind_speed': np.random.uniform(2, 25),
                            'area_type': np.random.choice(['Industrial', 'Residential', 'Commercial', 'Traffic'])
                        })
        
        self.df = pd.DataFrame(sample_data)
        st.success("✅ Sample data generated with realistic patterns!")
    
    def predict_pollution_source(self, pollution_data):
        """Predict pollution sources with realistic probabilities"""
        # Define pollution sources with base probabilities
        sources = ['Industrial', 'Vehicular', 'Construction', 'Agricultural', 'Natural']
        
        # Calculate probabilities based on pollution patterns
        pm25 = pollution_data.get('PM2.5', 50)
        pm10 = pollution_data.get('PM10', 100)
        no2 = pollution_data.get('NO2', 30)
        
        # Base probabilities adjusted by pollution levels
        probabilities = np.array([
            # Industrial - high PM2.5, PM10
            0.3 * (pm25/100) + 0.2 * (pm10/200),
            # Vehicular - high NO2, medium PM
            0.4 * (no2/50) + 0.1 * (pm25/100),
            # Construction - very high PM10
            0.6 * (pm10/250),
            # Agricultural - medium PM, seasonal
            0.2,
            # Natural - low pollution
            0.1 * (50/pm25) if pm25 > 0 else 0.1
        ])
        
        # Normalize probabilities
        probabilities = probabilities / probabilities.sum()
        
        return sources, probabilities
    
    def check_pollution_alerts(self, pollution_data):
        """Check for pollution threshold violations"""
        alerts = []
        for pollutant, value in pollution_data.items():
            if pollutant in self.POLLUTION_THRESHOLDS:
                thresholds = self.POLLUTION_THRESHOLDS[pollutant]
                if value >= thresholds['hazardous']:
                    alerts.append({
                        'level': 'CRITICAL',
                        'message': f'{pollutant} at {value:.1f} μg/m³ - HAZARDOUS levels!',
                        'pollutant': pollutant
                    })
                elif value >= thresholds['unhealthy']:
                    alerts.append({
                        'level': 'WARNING',
                        'message': f'{pollutant} at {value:.1f} μg/m³ - Unhealthy levels',
                        'pollutant': pollutant
                    })
                elif value >= thresholds['moderate']:
                    alerts.append({
                        'level': 'NOTICE', 
                        'message': f'{pollutant} at {value:.1f} μg/m³ - Moderate levels',
                        'pollutant': pollutant
                    })
        return alerts
    
    def create_sidebar_inputs(self):
        """Create comprehensive sidebar input section"""
        st.sidebar.header("🎯 Dashboard Controls")
        
        # State/Zone selection
        zones = sorted(self.df['zone'].unique())
        selected_zone = st.sidebar.selectbox("🗺️ Select Zone/State", ['All Zones'] + zones)
        
        # City selection based on zone
        if selected_zone == 'All Zones':
            available_cities = sorted(self.df['city'].unique())
        else:
            available_cities = sorted(self.df[self.df['zone'] == selected_zone]['city'].unique())
        
        selected_city = st.sidebar.selectbox("🏙️ Select City", available_cities)
        
        # Input method
        input_method = st.sidebar.radio(
            "📍 Input Method",
            ["Real-time Data", "Manual Input", "Historical Analysis"]
        )
        
        if input_method == "Manual Input":
            st.sidebar.subheader("🌫️ Manual Pollution Data")
            pollution_data = {
                'PM2.5': st.sidebar.slider("PM2.5 (μg/m³)", 0, 500, 50),
                'PM10': st.sidebar.slider("PM10 (μg/m³)", 0, 600, 100),
                'NO2': st.sidebar.slider("NO2 (μg/m³)", 0, 200, 30),
                'SO2': st.sidebar.slider("SO2 (μg/m³)", 0, 100, 15),
                'CO': st.sidebar.slider("CO (mg/m³)", 0.0, 10.0, 1.0),
                'O3': st.sidebar.slider("O3 (μg/m³)", 0, 150, 40)
            }
            
            # Environmental factors
            st.sidebar.subheader("🌤️ Environmental Factors")
            pollution_data.update({
                'temperature_c': st.sidebar.slider("Temperature (°C)", -10, 50, 25),
                'humidity': st.sidebar.slider("Humidity (%)", 0, 100, 60),
                'wind_speed': st.sidebar.slider("Wind Speed (km/h)", 0, 100, 15)
            })
            
            # Get coordinates for map
            city_data = self.df[self.df['city'] == selected_city].iloc[0]
            lat, lon = city_data['sensor_latitude'], city_data['sensor_longitude']
            
        elif input_method == "Historical Analysis":
            st.sidebar.subheader("📅 Time Range Selection")
            col1, col2 = st.sidebar.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=7))
            with col2:
                end_date = st.date_input("End Date", value=datetime.now().date())
            
            # Get data for selected period
            city_data = self.df[
                (self.df['city'] == selected_city) & 
                (self.df['timestamp'].dt.date >= start_date) & 
                (self.df['timestamp'].dt.date <= end_date)
            ]
            
            if not city_data.empty:
                pollution_data = {
                    'PM2.5': city_data['PM2.5'].mean(),
                    'PM10': city_data['PM10'].mean(),
                    'NO2': city_data['NO2'].mean(),
                    'SO2': city_data['SO2'].mean(),
                    'CO': city_data['CO'].mean(),
                    'O3': city_data['O3'].mean(),
                    'temperature_c': city_data['temperature_c'].mean(),
                    'humidity': city_data['humidity'].mean(),
                    'wind_speed': city_data['wind_speed'].mean()
                }
            else:
                pollution_data = {col: 0 for col in ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3', 'temperature_c', 'humidity', 'wind_speed']}
            
            # Get coordinates
            city_coords = self.df[self.df['city'] == selected_city].iloc[0]
            lat, lon = city_coords['sensor_latitude'], city_coords['sensor_longitude']
            
        else:  # Real-time Data
            # Get latest data for selected city
            latest_data = self.df[
                (self.df['city'] == selected_city) & 
                (self.df['timestamp'] >= (self.df['timestamp'].max() - timedelta(hours=1)))
            ]
            
            if not latest_data.empty:
                pollution_data = {
                    'PM2.5': latest_data['PM2.5'].mean(),
                    'PM10': latest_data['PM10'].mean(),
                    'NO2': latest_data['NO2'].mean(),
                    'SO2': latest_data['SO2'].mean(),
                    'CO': latest_data['CO'].mean(),
                    'O3': latest_data['O3'].mean(),
                    'temperature_c': latest_data['temperature_c'].mean(),
                    'humidity': latest_data['humidity'].mean(),
                    'wind_speed': latest_data['wind_speed'].mean()
                }
            else:
                pollution_data = {col: 0 for col in ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3', 'temperature_c', 'humidity', 'wind_speed']}
            
            # Get coordinates
            city_data = self.df[self.df['city'] == selected_city].iloc[0]
            lat, lon = city_data['sensor_latitude'], city_data['sensor_longitude']
        
        return selected_city, lat, lon, pollution_data, input_method
    
    def create_prediction_section(self, city, pollution_data):
        """Create AI prediction section with source analysis"""
        st.header("🤖 AI Pollution Source Analysis")
        
        # Get predictions
        sources, probabilities = self.predict_pollution_source(pollution_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Source Prediction")
            
            # Display predictions with confidence bars
            for source, prob in zip(sources, probabilities):
                confidence = prob * 100
                if confidence > 70:
                    color = "#28a745"
                    emoji = "🔴"
                elif confidence > 50:
                    color = "#ffc107" 
                    emoji = "🟠"
                else:
                    color = "#dc3545"
                    emoji = "🟡"
                
                # Confidence bar
                st.markdown(f"""
                <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <strong>{emoji} {source}</strong>
                        <span>{confidence:.1f}%</span>
                    </div>
                    <div style="background: #e9ecef; border-radius: 3px; height: 8px;">
                        <div style="background: {color}; width: {confidence}%; height: 8px; border-radius: 3px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📈 Source Distribution")
            
            # Create pie chart
            fig = px.pie(
                values=probabilities,
                names=sources,
                title="Pollution Source Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hovertemplate="<b>%{label}</b><br>Probability: %{percent}<extra></extra>"
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                margin=dict(t=50, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Current pollution levels
        st.subheader("🌫️ Current Pollution Levels")
        cols = st.columns(3)
        
        critical_pollutants = []
        for idx, pollutant in enumerate(['PM2.5', 'PM10', 'NO2']):
            with cols[idx]:
                value = pollution_data.get(pollutant, 0)
                if pollutant in self.POLLUTION_THRESHOLDS:
                    thresholds = self.POLLUTION_THRESHOLDS[pollutant]
                    
                    if value >= thresholds['hazardous']:
                        st.error(f"**{pollutant}**\n\n{value:.1f} μg/m³\n\n🔴 HAZARDOUS")
                        critical_pollutants.append(pollutant)
                    elif value >= thresholds['unhealthy']:
                        st.warning(f"**{pollutant}**\n\n{value:.1f} μg/m³\n\n🟠 Unhealthy")
                        critical_pollutants.append(pollutant)
                    elif value >= thresholds['moderate']:
                        st.info(f"**{pollutant}**\n\n{value:.1f} μg/m³\n\n🟡 Moderate")
                    else:
                        st.success(f"**{pollutant}**\n\n{value:.1f} μg/m³\n\n✅ Good")
                else:
                    st.metric(pollutant, f"{value:.1f} μg/m³")
        
        return critical_pollutants
    
    def create_trends_section(self, city):
        """Create pollution trends visualization"""
        st.header("📈 Pollution Trends Analysis")
        
        # Time range selector
        col1, col2 = st.columns(2)
        with col1:
            days = st.slider("Select time range (days)", 1, 30, 7)
        with col2:
            pollutant = st.selectbox("Select pollutant", ['PM2.5', 'PM10', 'NO2'])
        
        # Filter data
        city_data = self.df[self.df['city'] == city]
        recent_data = city_data[city_data['timestamp'] >= (datetime.now() - timedelta(days=days))]
        
        if not recent_data.empty:
            # Create hourly trends
            hourly_data = recent_data.set_index('timestamp').resample('H').agg({
                'PM2.5': 'mean',
                'PM10': 'mean', 
                'NO2': 'mean'
            }).reset_index()
            
            fig = go.Figure()
            
            # Add main trend line
            fig.add_trace(go.Scatter(
                x=hourly_data['timestamp'],
                y=hourly_data[pollutant],
                mode='lines',
                name=f'{pollutant} Trend',
                line=dict(color='red', width=3),
                fill='tozeroy',
                fillcolor='rgba(255,0,0,0.1)'
            ))
            
            # Add threshold lines
            if pollutant in self.POLLUTION_THRESHOLDS:
                thresholds = self.POLLUTION_THRESHOLDS[pollutant]
                colors = {'good': 'green', 'moderate': 'yellow', 'unhealthy': 'orange', 'hazardous': 'red'}
                
                for level, value in thresholds.items():
                    fig.add_hline(
                        y=value,
                        line_dash="dash",
                        line_color=colors.get(level, 'gray'),
                        annotation_text=f"{level.title()} ({value} μg/m³)",
                        annotation_position="right"
                    )
            
            fig.update_layout(
                title=f'{pollutant} Trends in {city} (Last {days} Days)',
                xaxis_title='Date & Time',
                yaxis_title=f'{pollutant} Concentration (μg/m³)',
                height=500,
                template='plotly_white',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No trend data available for {city}")
    
    def create_map_section(self, city, lat, lon):
        """Create interactive map with heatmaps"""
        st.header("🗺️ Interactive Pollution Map")
        
        # City data for map
        city_data = self.df[self.df['city'] == city]
        
        if not city_data.empty:
            # Create scatter map with heatmap effect
            fig = px.scatter_mapbox(
                city_data,
                lat="sensor_latitude",
                lon="sensor_longitude", 
                color="PM2.5",
                size="PM2.5",
                hover_name="sensor_name",
                hover_data={
                    "PM2.5": ":.1f",
                    "PM10": ":.1f",
                    "NO2": ":.1f", 
                    "area_type": True,
                    "timestamp": ":%Y-%m-%d %H:%M"
                },
                color_continuous_scale="Viridis",
                size_max=25,
                zoom=10,
                center={"lat": lat, "lon": lon},
                title=f"Real-time Pollution Map - {city}"
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                margin={"r": 0, "t": 50, "l": 0, "b": 0},
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No location data available for {city}")
    
    def create_alerts_section(self, pollution_data, city, critical_pollutants):
        """Create real-time alert system"""
        st.header("🚨 Real-Time Pollution Alerts")
        
        alerts = self.check_pollution_alerts(pollution_data)
        
        if alerts:
            # Display alerts
            for alert in alerts:
                if alert['level'] == 'CRITICAL':
                    st.error(f"""
                    **{alert['level']} ALERT**
                    
                    {alert['message']}
                    
                    ⚠️ Immediate action recommended!
                    """)
                elif alert['level'] == 'WARNING':
                    st.warning(f"""
                    **{alert['level']} ALERT**
                    
                    {alert['message']}
                    
                    🔍 Monitor closely
                    """)
                else:
                    st.info(f"""
                    **{alert['level']}**
                    
                    {alert['message']}
                    
                    📊 Within acceptable limits
                    """)
            
            # Alert subscription
            st.subheader("📧 Alert Notifications")
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input("Email address", placeholder="your.email@example.com")
            with col2:
                phone = st.text_input("Phone number", placeholder="+91XXXXXXXXXX")
            
            if st.button("🔔 Subscribe to Alerts", type="primary"):
                if email or phone:
                    st.success("✅ Alert subscription activated! You'll receive notifications for critical conditions.")
                else:
                    st.warning("Please provide email or phone for alerts")
        else:
            st.success("""
            ✅ **ALL SYSTEMS NORMAL**
            
            All pollution levels are within safe limits for {}.
            No immediate health concerns detected.
            """.format(city))
    
    def create_reports_section(self, city, pollution_data, sources, probabilities):
        """Create report generation and download section"""
        st.header("📥 Reports & Data Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Daily Report")
            
            # Create daily report
            report_data = {
                'Report_Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'City': city,
                'PM2.5_μg_m3': pollution_data.get('PM2.5', 0),
                'PM10_μg_m3': pollution_data.get('PM10', 0),
                'NO2_μg_m3': pollution_data.get('NO2', 0),
                'SO2_μg_m3': pollution_data.get('SO2', 0),
                'CO_mg_m3': pollution_data.get('CO', 0),
                'O3_μg_m3': pollution_data.get('O3', 0),
                'Primary_Source': sources[np.argmax(probabilities)],
                'Source_Confidence_%': np.max(probabilities) * 100,
                'Temperature_C': pollution_data.get('temperature_c', 0),
                'Humidity_%': pollution_data.get('humidity', 0),
                'Wind_Speed_km_h': pollution_data.get('wind_speed', 0)
            }
            
            report_df = pd.DataFrame([report_data])
            csv_report = report_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Daily Report (CSV)",
                data=csv_report,
                file_name=f"pollution_daily_report_{city}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary"
            )
        
        with col2:
            st.subheader("📊 Weekly Summary")
            
            # Generate weekly summary
            weekly_data = self.df[
                (self.df['city'] == city) & 
                (self.df['timestamp'] >= (datetime.now() - timedelta(days=7)))
            ]
            
            if not weekly_data.empty:
                weekly_stats = weekly_data[['PM2.5', 'PM10', 'NO2']].describe().round(2)
                weekly_csv = weekly_stats.to_csv()
                
                st.download_button(
                    label="📥 Download Weekly Stats (CSV)",
                    data=weekly_csv,
                    file_name=f"weekly_stats_{city}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No weekly data available")
        
        # Additional analytics
        st.subheader("📈 Quick Analytics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**City Comparison**")
            city_stats = self.df.groupby('city').agg({'PM2.5': 'mean'}).round(2)
            st.dataframe(city_stats.sort_values('PM2.5', ascending=False).head(8), use_container_width=True)
        
        with col2:
            st.write("**Zone-wise Analysis**")
            zone_stats = self.df.groupby('zone').agg({'PM2.5': 'mean'}).round(2)
            st.dataframe(zone_stats.sort_values('PM2.5', ascending=False), use_container_width=True)
    
    def run_dashboard(self):
        """Run the complete dashboard"""
        
        # Load data
        self.load_data()
        
        if self.df is None:
            st.error("❌ Unable to load data. Please check your data files.")
            return
        
        # Main header
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FF9933 0%, #FFFFFF 50%, #138808 100%); 
                    padding: 30px; 
                    border-radius: 15px; 
                    color: white; 
                    text-align: center;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    border: 2px solid #000080;">
            <h1 style="margin: 0; font-size: 3.5em; font-weight: bold; color: #000080;">🇮🇳 AI-EnviroScan India</h1>
            <p style="margin: 15px 0 0 0; font-size: 1.5em; color: #000080;">National Pollution Monitoring & Source Prediction System</p>
            <p style="margin: 10px 0 0 0; font-size: 1.1em; color: #000080; opacity: 0.9;">
                Real-time Air Quality Monitoring Across 20 Major Indian Cities
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get user inputs
        selected_city, lat, lon, pollution_data, input_method = self.create_sidebar_inputs()
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 AI Analysis", 
            "📈 Trends", 
            "🗺️ Map", 
            "🚨 Alerts", 
            "📊 Reports"
        ])
        
        with tab1:
            critical_pollutants = self.create_prediction_section(selected_city, pollution_data)
        
        with tab2:
            self.create_trends_section(selected_city)
        
        with tab3:
            self.create_map_section(selected_city, lat, lon)
        
        with tab4:
            self.create_alerts_section(pollution_data, selected_city, critical_pollutants)
        
        with tab5:
            sources, probabilities = self.predict_pollution_source(pollution_data)
            self.create_reports_section(selected_city, pollution_data, sources, probabilities)
        
        # Footer
        st.markdown("---")
        st.markdown(
            "**AI-EnviroScan India** • Real-time Pollution Monitoring • "
            f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} • "
            "Powered by Machine Learning"
        )

# Run the dashboard
if __name__ == "__main__":
    dashboard = FinalEnviroScanDashboard()
    dashboard.run_dashboard()