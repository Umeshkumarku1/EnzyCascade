import streamlit as st
import pandas as pd
import os

# Set config immediately
st.set_page_config(page_title="EnzyCascade™", layout="wide")

# Database Path
DB_PATH = "phenotype_database-v2.xlsx"

@st.cache_data
def load_data():
    if not os.path.exists(DB_PATH):
        return None
    try:
        # engine='openpyxl' is required for .xlsx files
        return pd.read_excel(DB_PATH, engine='openpyxl')
    except Exception as e:
        st.error(f"Error loading Excel: {e}")
        return None

df = load_data()

# Only render UI if data loaded
if df is not None:
    st.markdown('<p style="font-size: 2.8rem; font-weight: 800; color: #1E3A8A;">EnzyCascade™</p>', unsafe_html=True)
    st.markdown("---")
    st.write("Database loaded successfully.")
    # Add the rest of your app logic here...
else:
    st.error("Database could not be loaded. Ensure 'phenotype_database-v2.xlsx' is in the root and 'openpyxl' is in requirements.txt.")
