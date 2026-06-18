"""First starter apps, based on streamlit tutorials
"""

# Standard library imports
import logging
import pathlib

# Third party imports
import pandas as pd
import numpy as np
import streamlit as st

# Local imports
import bootstrap

# Constants
SERVICE_NAME = pathlib.Path(__file__).stem
TIMESTAMP_COLUMN = bootstrap.UBER_RAW_DATA_DATE_COLUMN

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(bootstrap.UBER_RAW_DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[TIMESTAMP_COLUMN] = pd.to_datetime(data[TIMESTAMP_COLUMN])
    return data

def main(logger: logging.Logger):
  st.title("Uber pickups in NYC")
  data_load_state = st.text("Loading data ...")
  data = load_data(10_000)
  data_load_state .text("Loading data done !")
  
  # Raw data inspection
  if st.checkbox('Show raw data'):
    st.subheader("Raw data")
    st.write(data)
  
  # Histogram
  st.subheader('Number of pickups by hour')
  hist_values = np.histogram(data[TIMESTAMP_COLUMN].dt.hour, 
                             bins=24, range=(0,24))[0]
  st.bar_chart(hist_values)

  # Plot data on map
  st.subheader("Map of all pickups")
  st.map(data)
  
  # Plot data at specific hours
  hour_to_filter = st.slider('hour', 0, 23, 17)
  filtered_data = data[data[TIMESTAMP_COLUMN].dt.hour == hour_to_filter]
  st.subheader(f"Map of all pickups at {hour_to_filter}:00")
  st.map(filtered_data)
  

if __name__ == "__main__":
  with bootstrap.ServiceContainer(service_name=SERVICE_NAME) as service_container:
    main(service_container.root_logger)