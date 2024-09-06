import streamlit as st
from ee_authenticate import authenticate
import ee
import geemap.foliumap as geemap
from datetime import datetime, timedelta
import streamlit_folium as st_folium

# Authenticate with Google Earth Engine
authenticate()

# Set page configuration
st.set_page_config(
    page_title="Satkhira Soil Salinity Monitoring",
    page_icon="🌍",
    layout="wide",
)

# Sidebar content
with st.sidebar:
    st.image('logo.png', width=250)
    st.header('🌾 Real-Time Soil Salinity Monitoring in Satkhira')
    # st.markdown("""
    # **Welcome to Team Urbor's innovative solution for farmers in Satkhira!**
    
    # Our system provides up-to-date soil salinity monitoring and predictions using advanced satellite imagery, empowering farmers to make informed decisions.

    # ### Supported By:
    # """)
    st.write('Supported by')
    st.image('support_logo.png', width=200)
    st.markdown("---")
    st.write("Navigate through the app using the options below:")

# Main content header
st.image('poster.png')
st.header('🌍 Real-Time Soil Salinity Monitoring Dashboard')
# st.image('poster.png')
st.markdown("""
### Overview
Satkhira's coastal region faces significant challenges due to soil salinity, which impacts agricultural productivity. This dashboard provides a real-time soil salinity index (SSI) visualization to help farmers and stakeholders monitor and manage soil health effectively.

**Instructions:**
- The map below displays the Satkhira subdivision. Use the interactive map to explore the region.
- The SSI heatmap indicates areas with varying salinity levels. Blue represents low salinity, white indicates moderate salinity, and red signifies high salinity.

Explore the tools provided to monitor and predict soil salinity, helping to ensure sustainable farming practices in the region.
""")

# Load Satkhira subdivision boundary
@st.cache_data
def get_satkhira_boundary():
    return ee.FeatureCollection('FAO/GAUL/2015/level2') \
        .filter(ee.Filter.And(
            ee.Filter.eq('ADM0_NAME', 'Bangladesh'),
            ee.Filter.eq('ADM1_NAME', 'Khulna'),
            ee.Filter.eq('ADM2_NAME', 'Satkhira')
        ))

satkhira = get_satkhira_boundary()

# Function to calculate SSI
def calculate_ssi(image):
    ssi = image.expression(
        '(B11 - B8) / (B11 + B8)',
        {
            'B11': image.select('SR_B3'),
            'B8': image.select('SR_B4')
        }
    ).rename('SSI')
    return ssi

# Calculate SSI over Satkhira
def get_satkhira_ssi():
    # Define time range (last 6 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Load and filter Sentinel-2 imagery
    s2 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
        .filterBounds(satkhira) \
        .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
        .median()
    
    # Calculate SSI for the image
    ssi_satkhira = calculate_ssi(s2).clip(satkhira)
    return ssi_satkhira

# Display the map
st.subheader('🌐 Satkhira Soil Salinity Heatmap')
st.write("Zoom and pan to explore different areas of Satkhira. The heatmap shows the soil salinity index based on recent satellite data.")

mgee = geemap.Map(center=[22.35, 89.08], zoom=10, height="300px", width="200px")
mgee.addLayer(satkhira.style(**{'fillColor': '00000000', 'color': '4F8BF9'}), {}, 'Satkhira Subdivision')

ssi_image = get_satkhira_ssi()
ssi_vis_params = {
    'min': -0.1,
    'max': 0.1,
    'palette': ['blue', 'white', 'red']
}

mgee.addLayer(ssi_image, ssi_vis_params, 'SSI Heatmap')
mgee.to_streamlit(height=600, width=900)

st.markdown("""
**Note:** The color intensity on the map represents the severity of soil salinity. The data is updated every six months to reflect recent changes.
""")
