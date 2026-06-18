"""A dashboard to explore data from Kaggle public repository
"""

# Standard libarary import
import io
import logging
import os
import pathlib

# Third party imports
import kagglehub
import pandas as pd
import numpy as np
import streamlit as st

# Local import
import bootstrap


# Constants
SERVICE_NAME = pathlib.Path(__file__).stem
KAGGLE_DATA_DIR = os.getenv('KAGGLE_DATA_DIR', 'kaggle_datasets')

DEF_DATASET_HANDLE = "liqiang2022/gold-price-of-china-full-data-20152022"

@st.cache_data
def download_data_locally(data_handle:str)->dict[str, pathlib.Path]:
    data_path = pathlib.Path(data_handle)
    data_dir = pathlib.Path(KAGGLE_DATA_DIR).joinpath(*(data_path.parts[:-1]))
    os.makedirs(data_dir, exist_ok=True)
    if os.path.exists(data_dir):
        result = {x:data_dir.joinpath(x).absolute() for x in os.listdir(data_dir) if not x.startswith(".")}
        if len(result) > 0:
            print("Using locally downloaded data !")
            return result
    
    print("Start download data from kaggle")
    kagglehub.dataset_download(data_handle, output_dir=str(data_dir))
    result = {x:data_dir.joinpath(x).absolute() for x in os.listdir(data_dir) if not x.startswith(".")}
    return result

@st.cache_data
def load_data(data_path:str)->pd.DataFrame:
    df = pd.read_csv(data_path, )
    lowercase = lambda x: str(x).lower()
    df.rename(lowercase, axis='columns', inplace=True)
    # find index if one existed
    if df.columns[0].startswith("unnamed"):
        df.set_index(df.columns[0], inplace=True)
    # Convert date
    for col in df.columns:
        if "date" in col:
            df[col] = pd.to_datetime(df[col])
    return df


@st.dialog("Select data set")
def select_dataset_dialog():
    current_dataset = st.session_state.dataset_handle
    if current_dataset == "NONE":
        current_dataset = DEF_DATASET_HANDLE
    dataset_handle = st.text_input("Please enter the dataset handle: ", 
                                   value=current_dataset)
    if (not dataset_handle) or dataset_handle.upper() == "NONE":
        st.selectbox("Dataset file", options=[], placeholder="None")
        return
    # we have a valid dataset here
    st.session_state.dataset_handle = dataset_handle
    dataset_file_map = download_data_locally(st.session_state.dataset_handle)
    st.session_state.dataset_file_map = dataset_file_map
    # Prepare to select the file in this dataset
    file_list = list(st.session_state["dataset_file_map"].keys())
    file_list.sort()
    current_selection = 0
    if "dataset_file_selection" in st.session_state \
        and st.session_state.dataset_file_selection in file_list:
        current_selection = file_list.index(st.session_state.dataset_file_selection)
    selection = st.selectbox("Dataset file", index=current_selection, options=file_list)
    if st.button("Start"):
        st.session_state.dataset_file_selection = selection
        st.rerun()


@st.fragment
def create_metadata_container():
    container = st.container(border=True)
    data_df = st.session_state.get("data_df", None)
    if data_df is None:
        return
    buffer = io.StringIO()
    data_df.info(buf=buffer)
    container.code(buffer.getvalue())
    with container.expander("Column details"):
        column_names = list(data_df.columns)
        tabs = st.tabs(column_names)
        for i in range(len(tabs)):
            col_name = column_names[i]
            tabs[i].header(col_name)
            tabs[i].write(data_df[col_name].describe(include='all'))

def main(logger: logging.Logger):
    
    if "dataset_handle" not in st.session_state or st.session_state.dataset_handle == "":
        st.session_state.dataset_handle = "NONE"
    if "dataset_file_selection" not in st.session_state:
        st.session_state.dataset_file_selection = "NONE"
    if "dataset_file_map" not in st.session_state:
        st.session_state.dataset_file_map = {}
    
    st.title("Kaggle data exploration")
    
    dataset_container = st.container(border=True)
    dataset_container.subheader("Dataset selection")
    dataset_container.markdown(f"**Dataset Handle**: :blue-badge[{st.session_state.dataset_handle}]")
    dataset_container.markdown(f"\t**Selected File**: :green-badge[{st.session_state.dataset_file_selection}]")
    
    dataset_container.button("Select dataset", on_click=select_dataset_dialog)
    
    if st.session_state.dataset_file_selection:
        file_selection = st.session_state.dataset_file_selection
        if file_selection in st.session_state.dataset_file_map:
            data_path = st.session_state.dataset_file_map[file_selection]
            st.session_state.data_df = load_data(data_path)
        
    create_metadata_container()
    
    
if __name__ == "__main__":
    with bootstrap.ServiceContainer(service_name=SERVICE_NAME) as service_container:
        main(service_container.root_logger)