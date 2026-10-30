# [IA] Claude Code – leitura do csv com cache
import pandas as pd
import streamlit as st


@st.cache_data(max_entries=4)
def load_data(path="data/clean/dataset.csv"):
    return pd.read_csv(path)
