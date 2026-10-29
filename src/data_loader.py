import pandas as pd
import streamlit as st

# Caminho relativo à raiz do repositório: funciona local e no Streamlit Community Cloud
CAMINHO_DATASET = "data/clean/dataset.csv"


@st.cache_data(max_entries=4)
def load_data(path=CAMINHO_DATASET):
    """Lê o dataset já tratado (exportado ao final de notebooks/eda-com-downloads.ipynb).

    Com @st.cache_data o CSV é lido uma vez só e reaproveitado entre as interações.
    """
    return pd.read_csv(path)
