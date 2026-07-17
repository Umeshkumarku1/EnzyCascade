import streamlit as st
import pandas as pd
import os

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="EnzyCascade™ | Diagnostic Portal", page_icon="🧬", layout="wide")

# 2. Database Loader
DB_PATH = "phenotype_database-v2.xlsx"

@st.cache_data
def get_data():
    if not os.path.exists(DB_PATH):
        return None
    try:
        # engine='openpyxl' is essential for .xlsx files
        return pd.read_excel(DB_PATH, engine='openpyxl')
    except Exception:
        return None

# Load data
df = get_data()

# 3. Guard Clause: Stop execution if data is missing
if df is None:
    st.error(f"⚠️ Critical Error: '{DB_PATH}' not found or invalid. Ensure the file is in the root and 'openpyxl' is in requirements.txt.")
    st.stop()

# 4. Main Application UI (Only renders if data is valid)
st.markdown('<p style="font-size: 2.8rem; font-weight: 800; color: #1E3A8A;">EnzyCascade™</p>', unsafe_allow_html=True)
st.markdown("---")

# Logic to extract features
feature_list = [c for c in df.columns if "strain" not in c.lower() and "name" not in c.lower()]

# --- UI Inputs ---
user_inputs = {}
col1, col2, col3 = st.columns(3)

with col1:
    g_choice = st.selectbox("Gram stain:", ["Not Performed", "Gram-negative", "Gram-positive"])
    user_inputs["Gram stain"] = "gramnegativenegative" if g_choice == "Gram-negative" else ("positive" if g_choice == "Gram-positive" else -1.0)
with col2:
    s_choice = st.selectbox("Shape / Morphology:", ["Not Performed", "Rod", "Coccus", "Filamentous"])
    user_inputs["Shape"] = s_choice.lower() if s_choice != "Not Performed" else -1.0
with col3:
    c_choice = st.selectbox("Pigmentation / Color:", ["Not Performed", "white", "yellow", "gray", "green", "pink", "red"])
    user_inputs["color"] = c_choice.lower() if c_choice != "Not Performed" else -1.0

# Enzyme Matrix Display
remaining_features = [f for f in feature_list if f not in ["Gram stain", "Shape", "color"]]
cols = st.columns(4)
for i, feat in enumerate(remaining_features):
    with cols[i % 4]:
        val = st.selectbox(f"{feat}:", ["Not Performed", "Negative", "Variable", "Positive"], key=f"ui_{feat}")
        user_inputs[feat] = val.lower() if val != "Not Performed" else -1.0

# --- Execution Engine ---
if st.button("🚀 Execute EnzyCascade™ Mapping"):
    strain_col = [c for c in df.columns if "strain" in c.lower() or "name" in c.lower()][0]
    results = []
    
    for _, row in df.iterrows():
        score = 0.0
        # Score Physical Traits
        for p in ["Gram stain", "Shape", "color"]:
            db_v = str(row.get(p, "")).lower() if not pd.isna(row.get(p)) else ""
            if user_inputs[p] != -1.0 and user_inputs[p] == db_v: score += (30.0 if p == "color" else 20.0)
            elif user_inputs[p] == -1.0: score += (30.0 if p == "color" else 20.0)
        
        # Score Enzyme Matrix
        e_match, e_total = 0, 0
        for f, v in user_inputs.items():
            if f not in ["Gram stain", "Shape", "color"] and v != -1.0:
                e_total += 1
                if str(row.get(f, "")).lower() == v: e_match += 1
        score += (e_match / e_total * 30.0) if e_total > 0 else 30.0
        
        results.append({"Strain": str(row[strain_col]).title(), "Match_Percent": round(score, 2)})
    
    res = pd.DataFrame(results).sort_values("Match_Percent", ascending=False).head(3)
    res.columns = ["Strain", "Match (%)"]
    st.dataframe(res, use_container_width=True)
