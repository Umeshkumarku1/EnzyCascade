import streamlit as st
import pandas as pd
import os

# 1. Absolute first call
st.set_page_config(page_title="EnzyCascade™ | Diagnostic Portal", page_icon="🧬", layout="wide")

# 2. Database Loader
DB_PATH = "phenotype_database-v2.xlsx"
COMMUNITY_TXT_PATH = "bacterial community.txt"

def load_data():
    if not os.path.exists(DB_PATH):
        return None
    try:
        return pd.read_excel(DB_PATH, sheet_name=0)
    except:
        return None

# 3. Execution Gate
df = load_data()

if df is None:
    st.error(f"⚠️ Critical Error: '{DB_PATH}' was not found in the root directory. Please upload it to your GitHub repository.")
    st.stop()

# 4. UI Rendering (Only runs if df is not None)
st.markdown('<p style="font-size: 2.8rem; font-weight: 800; color: #1E3A8A;">EnzyCascade™</p>', unsafe_html=True)
st.markdown("---")

# ... [Keep your existing sidebar and main logic here] ...
