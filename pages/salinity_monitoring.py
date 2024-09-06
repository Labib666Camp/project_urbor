import streamlit as st
from streamlit_folium import st_folium
import folium
import ee
import numpy as np
import geemap
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from streamlit_extras import stylable_container

# print('starting Initialization')
# ee.Initialize(project='ee-workmainulislam2')
# print('Initialized')
st.set_page_config(page_title="Salinity Monitoring", page_icon="📈",layout='wide')
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


def calculate_ssi(image):
    ssi = image.expression(
        '(B11 - B8) / (B11 + B8)',
        {
            'B11': image.select('B11'),
            'B8': image.select('B8')
        }
    ).rename('SSI')
    return image.addBands(ssi)

# Function to get SSI time series for a district
def get_ssi_time_series(district):
    # geometry = district.geometry()
    # print(geometry)
    geometry = district

    # Define time range (last 6 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    # Load and filter Sentinel-2 imagery
    s2 = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
        .filterBounds(geometry) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))

    # Calculate SSI for each image
    ssi_collection = s2.map(calculate_ssi)

    # Function to extract date and mean SSI for the district
    def extract_ssi(image):
        date = image.date().format('YYYY-MM-dd')
        mean_ssi = image.select('SSI').reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=100
        ).get('SSI')
        return ee.Feature(None, {'date': date, 'SSI': mean_ssi})

    # Extract time series
    time_series = ssi_collection.map(extract_ssi).getInfo()

    # Convert to pandas DataFrame
    df = pd.DataFrame([
        {'date': feature['properties']['date'], 'SSI': feature['properties']['SSI']}
        for feature in time_series['features']
        if feature['properties']['SSI'] is not None
    ])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    return df

def get_coords(output):
    # Display the map in Streamlit
    # output = st_folium(m, width=700, height=500)

    # Check if a polygon has been drawn
    if output and output['last_active_drawing']:
        geometry = output['last_active_drawing']['geometry']

        if geometry['type'] == 'Polygon':
            polygon_coords = geometry['coordinates'][0]
            print(polygon_coords)
            roi = ee.Geometry.Polygon(polygon_coords)
            return roi
        else:
            return None
    else:
        return None

def get_plot_time_series(roi):
    nssi_df = get_ssi_time_series(roi)
    # Plot time series
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=nssi_df['date'], y=nssi_df['SSI'], mode='lines+markers'))
    fig.update_layout(
        title='Soil Salinity Index Time Series (Last 6 Months)',
        xaxis_title='Date',
        yaxis_title='Soil Salinity Index',
        height=400,
        width = 500,
    )
    st.plotly_chart(fig, use_container_width=True)


col1,col2 = st.columns(2)
roi = None

with col1:
    # with st.container(border=True):
    m = folium.Map(location=[22.7217, 89.9082], zoom_start=8)
    folium.plugins.Draw(export=True).add_to(m)
    output = st_folium(m, width=700, height=500)
    status = output['last_active_drawing']
    # print(status['geometry']['coordinates'][0])
    if output and output['last_active_drawing']:
        roi = get_coords(output)
        print(status['geometry']['coordinates'][0])

with col2:
    # Main content header
    st.header("🌍 Soil Salinity Monitoring Dashboard")
    st.markdown("""
    ### Overview
    This tool allows users to monitor and analyze the soil salinity index (SSI) over the past six months in the Satkhira region. Follow the steps below to interact with the map and generate time-series data.

    **Instructions:**
    1. Zoom into the area of interest within the map below.
    2. Draw a rectangular box around the region you want to analyze.
    3. Click "Analyze" to generate and view the SSI time series for the last six months.
    """)

    if roi:
        with st.status('Calculating....'):
            with st.popover('Analyze'):
                get_plot_time_series(roi)
                roi = None
