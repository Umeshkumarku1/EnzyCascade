import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
import time

# Set modern, wide page layout
st.set_page_config(
    page_title="EnzyCascade™ | AI Diagnostic Portal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Tech Minimalist Styling
st.markdown("""
    <style>
        .main-title { font-size: 2.8rem !important; font-weight: 800 !important; color: #1E3A8A; margin-bottom: 0px !important; }
        .tagline { font-size: 1.1rem !important; font-style: italic; color: #4B5563; margin-bottom: 20px !important; }
        .section-header { font-size: 1.4rem !important; font-weight: 600 !important; color: #2563EB; margin-top: 20px !important; }
        .stButton>button { background-color: #2563EB !important; color: white !important; border-radius: 8px !important; font-weight: 600 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">EnzyCascade™</p>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Rule-Based Enzyme Cascade Bacterial Identification System</p>', unsafe_allow_html=True)
st.markdown("---")

# UPDATED PATHS: Pointing to root directory
RULE_PATH = "phenotype_database-v2.xlsx"
PHENO_PATH = "phenotype_database-v2.xlsx"
MODEL_PATH = "bacterial_rf_model.pkl"
COMMUNITY_TXT_PATH = "bacterial community.txt"

@st.cache_resource
def load_ml_assets():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(PHENO_PATH):
        return None, None
    try:
        df_p = pd.read_excel(PHENO_PATH, sheet_name=0)
        features = [col for col in df_p.columns if col != 'strains.Full Scientific Name']
        model = joblib.load(MODEL_PATH)
        return features, model
    except Exception:
        return None, None

def load_allowed_community():
    if os.path.exists(COMMUNITY_TXT_PATH):
        try:
            with open(COMMUNITY_TXT_PATH, 'r', encoding='utf-8') as f:
                return [line.strip().lower() for line in f.readlines() if line.strip()]
        except Exception:
            return []
    return []

def fetch_bacterial_profile_from_web(strain_name):
    # Simulated web hook
    if "baumannii" in strain_name or "acinetobacter" in strain_name:
        return {"Gram stain": "gramnegativenegative", "Shape": "rod", "color": "white"}
    elif "aureus" in strain_name or "staphylococcus" in strain_name:
        return {"Gram stain": "positive", "Shape": "coccus", "color": "yellow"}
    return {}

try:
    feature_list, clf = load_ml_assets()
    allowed_community = load_allowed_community()
    
    if feature_list is None:
        st.error("⚠️ Database connection failed. Ensure `phenotype_database-v2.xlsx` and `bacterial_rf_model.pkl` are in the main project folder.")
        st.stop()

    with st.sidebar:
        st.markdown("### 📊 Engine Status")
        st.success("Database Status: Connected")
        enable_web_lookup = st.checkbox("Enable Automated Web Profile Fetching", value=True)
        st.markdown("---")
        st.markdown("### ⚙️ Scoring Thresholds")
        st.markdown("- **Gram/Shape/Color:** 70 pts\n- **Enzyme Cascades:** 30 pts")

    st.markdown('<p class="section-header">📋 Phase 1: Observed Laboratory Profiles</p>', unsafe_allow_html=True)
    user_inputs = {}

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            choice = st.selectbox("Gram stain:", ["Not Performed", "Gram-negative", "Gram-positive"])
            user_inputs["Gram stain"] = "gramnegativenegative" if choice == "Gram-negative" else ("positive" if choice == "Gram-positive" else -1.0)
        with col2:
            choice = st.selectbox("Shape / Morphology:", ["Not Performed", "Rod", "Coccus", "Filamentous"])
            user_inputs["Shape"] = choice.lower() if choice != "Not Performed" else -1.0
        with col3:
            choice = st.selectbox("Pigmentation / Color:", ["Not Performed", "white", "yellow", "gray", "green", "pink", "red"])
            user_inputs["color"] = choice.lower() if choice != "Not Performed" else -1.0

    st.markdown('<p class="section-header">🧬 Phase 2: Secondary Enzyme Cascade Matrix</p>', unsafe_allow_html=True)
    remaining_features = sorted([f for f in feature_list if f not in ["Gram stain", "Shape", "color"]])
    
    tab1, tab2, tab3, tab4 = st.tabs(["[A-D]", "[E-L]", "[M-R]", "[S-Z]"])
    for tab, features in zip([tab1, tab2, tab3, tab4], [remaining_features[0:len(remaining_features)//4], ...]): # Logic wrapper
        with tab:
            cols = st.columns(4)
            for j, feat in enumerate(remaining_features):
                with cols[j % 4]:
                    val = st.selectbox(f"{feat}:", ["Not Performed", "Negative", "Variable", "Positive"], key=f"ui_{feat}")
                    user_inputs[feat] = val.lower() if val != "Not Performed" else -1.0

    if st.button("🚀 Execute EnzyCascade™ Mapping", use_container_width=True):
        rules_df = pd.read_excel(PHENO_PATH, sheet_name=0)
        strain_col = [c for c in rules_df.columns if "strain" in c.lower() or "name" in c.lower()][0]
        
        results = []
        for idx, row in rules_df.iterrows():
            strain_name = str(row[strain_col]).lower()
            if allowed_community and not any(item in strain_name for item in allowed_community): continue
            
            score, web = 0.0, fetch_bacterial_profile_from_web(strain_name) if enable_web_lookup else {}
            
            for p in ["Gram stain", "Shape", "color"]:
                db_v = str(row.get(p, "")).lower() if not pd.isna(row.get(p)) else web.get(p, "")
                if user_inputs[p] != -1.0 and user_inputs[p] == db_v: score += 20.0 if p != "color" else 30.0
                elif user_inputs[p] == -1.0: score += 20.0 if p != "color" else 30.0
            
            e_match, e_total = 0, 0
            for f, v in user_inputs.items():
                if f not in ["Gram stain", "Shape", "color"] and v != -1.0:
                    e_total += 1
                    if str(row.get(f, "")).lower() == v: e_match += 1
            score += (e_match / e_total * 30.0) if e_total > 0 else 30.0
            results.append({"Strain": strain_name.title(), "Match (%)": round(score, 2)})
            
        res = pd.DataFrame(results).sort_values("Match (%)", ascending=False).head(3)
        st.success("Diagnostic Mapping Complete!")
        st.dataframe(res, use_container_width=True)

except Exception as e:
    st.error(f"Engine Failure: {e}")
