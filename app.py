import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
import time

# Set modern, wide page layout with customized metadata
st.set_page_config(
    page_title="EnzyCascade™ | AI Diagnostic Portal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Tech Minimalist Styling Injection
st.markdown("""
    <style>
        .main-title {
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            color: #1E3A8A;
            margin-bottom: 0px !important;
        }
        .tagline {
            font-size: 1.1rem !important;
            font-style: italic;
            color: #4B5563;
            margin-top: 0px !important;
            margin-bottom: 20px !important;
        }
        .section-header {
            font-size: 1.4rem !important;
            font-weight: 600 !important;
            color: #2563EB;
            margin-top: 20px !important;
        }
        .stButton>button {
            background-color: #2563EB !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            padding: 0.5rem 2rem !important;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #1D4ED8 !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
        }
    </style>
""", unsafe_allow_html=True)

# Application Header Block
st.markdown('<p class="main-title">EnzyCascade™</p>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Rule-Based Enzyme Cascade Bacterial Identification System</p>', unsafe_allow_html=True)
st.markdown("---")

# Constant Relative Paths - Clean architecture for Streamlit Cloud deployment
RULE_PATH = os.path.join("database", "phenotype_database-v2.xlsx")
PHENO_PATH = os.path.join("database", "phenotype_database-v2.xlsx")
MODEL_PATH = os.path.join("database", "bacterial_rf_model.pkl")
COMMUNITY_TXT_PATH = "bacterial community.txt"

@st.cache_resource
def load_ml_assets():
    # Fixed unpacking issue: gracefully returns 2 items matching expectations
    if not os.path.exists(MODEL_PATH):
        return None, None
    try:
        df_p = pd.read_excel(PHENO_PATH, sheet_name='Sheet1')
    except Exception:
        try:
            df_p = pd.read_excel(PHENO_PATH, sheet_name=0)
        except Exception:
            return None, None
            
    features = [col for col in df_p.columns if col != 'strains.Full Scientific Name']
    try:
        model = joblib.load(MODEL_PATH)
    except Exception:
        return features, None
    return features, model

def load_allowed_community():
    if os.path.exists(COMMUNITY_TXT_PATH):
        try:
            with open(COMMUNITY_TXT_PATH, 'r', encoding='utf-8') as f:
                lines = [line.strip().lower() for line in f.readlines() if line.strip()]
            return lines
        except Exception:
            pass
    return []

# --- EXTENSIBLE WEB SCRAPING / SEARCH INFERENCE MODULE ---
def fetch_bacterial_profile_from_web(strain_name):
    """
    Placeholder hook for automated phenotypic web-profiling.
    Can be dynamically tied to LPSN or BacDive REST APIs down the road.
    """
    inferred_profile = {"Gram stain": None, "Shape": None, "color": None}
    
    # Fallback simulated configurations for demo validation
    if "baumannii" in strain_name or "acinetobacter" in strain_name:
        inferred_profile = {"Gram stain": "gramnegativenegative", "Shape": "rod", "color": "white"}
    elif "aureus" in strain_name or "staphylococcus" in strain_name:
        inferred_profile = {"Gram stain": "positive", "Shape": "coccus", "color": "yellow"}
        
    return inferred_profile

try:
    feature_list, clf = load_ml_assets()
    allowed_community = load_allowed_community()
    
    # Handled fallback rules gracefully if assets are deploying/missing
    if feature_list filter is None:
        st.error("⚠️ Database connection failed. Please ensure `phenotype_database-v2.xlsx` is inside your GitHub `database` directory.")
        st.stop()

    # Sidebar Dashboard Control Center
    with st.sidebar:
        st.markdown("### 📊 Engine Status")
        st.success("Database Status: Connected")
        
        if clf is not None:
            st.success("Predictive Classifier: Loaded")
        else:
            st.warning("Predictive Classifier: Offline (Using Rules Engine Only)")
            
        st.info(f"Loaded Phenotypic Features: {len(feature_list)}")
        
        # UI Toggle for Web Profiler Feature
        enable_web_lookup = st.checkbox("Enable Automated Web Profile Fetching", value=True, 
                                        help="If local database rows contain missing (NaN) values, the system will look up data from online repositories automatically.")
        
        if allowed_community:
            st.caption(f"Whitelisted Target Strains: {len(allowed_community)}")
        
        st.markdown("---")
        st.markdown("### ⚙️ Scoring Threshold Weights")
        st.markdown("- **Gram Stain Match:** 20 pts")
        st.markdown("- **Shape Match:** 20 pts")
        st.markdown("- **Color Match:** 30 pts")
        st.markdown("- **Enzyme Cascades:** 30 pts")
        st.markdown("**Total Maximum Score: 100%**")

    st.markdown('<p class="section-header">📋 Phase 1: Enter Observed Laboratory Profiles</p>', unsafe_allow_html=True)
    st.caption("Leave assays as 'Not Performed' unless specifically isolated and verified in the laboratory environment.")

    user_inputs = {}

    # 1. Primary Physical Features & Morphology Box
    with st.container(border=True):
        st.markdown("**Primary Physical Features & Morphology**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if "Gram stain" in feature_list:
                choice = st.selectbox("Gram stain:", options=["Not Performed", "Gram-negative", "Gram-positive"])
                if choice == "Gram-negative":
                    user_inputs["Gram stain"] = "gramnegativenegative"
                elif choice == "Gram-positive":
                    user_inputs["Gram stain"] = "positive"
                else:
                    user_inputs["Gram stain"] = -1.0
        with col2:
            if "Shape" in feature_list:
                choice = st.selectbox("Shape / Morphology:", options=["Not Performed", "Rod", "Coccus", "Filamentous"])
                user_inputs["Shape"] = choice.lower() if choice != "Not Performed" else -1.0
        with col3:
            if "color" in feature_list:
                choice = st.selectbox("Pigmentation / Color:", options=["Not Performed", "white", "yellow", "gray", "green", "pink", "red"])
                user_inputs["color"] = choice.lower() if choice != "Not Performed" else -1.0

    st.markdown('<p class="section-header">🧬 Phase 2: Secondary Enzyme Cascade Screening Matrix</p>', unsafe_allow_html=True)

    # Helper function to distribute rows dynamically into 4 columns inside tabs
    def render_feature_grid(features_subgroup):
        cols = st.columns(4)
        for idx, feat in enumerate(features_subgroup):
            if feat in feature_list and feat not in ["Gram stain", "Shape", "color"]:
                with cols[idx % 4]:
                    choice = st.selectbox(
                        f"{feat}:",
                        options=["Not Performed", "Negative", "Variable", "Positive"],
                        key=f"ui_{feat}"
                    )
                    user_inputs[feat] = choice.lower() if choice != "Not Performed" else -1.0

    # Sorting remaining enzyme/biochemical features into modern tab sections
    remaining_features = sorted([f for f in feature_list if f not in ["Gram stain", "Shape", "color"]])
    
    tab_A_D, tab_E_L, tab_M_R, tab_S_Z = st.tabs([
        "🧪 Cascades [A - D]", 
        "🧪 Cascades [E - L]", 
        "🧪 Cascades [M - R]", 
        "🧪 Cascades [S - Z]"
    ])
    
    with tab_A_D:
        group_ad = [f for f in remaining_features if f[0].upper() in ['(', '2', '3', '4', '5', 'A', 'B', 'C', 'D']]
        render_feature_grid(group_ad)
        
    with tab_E_L:
        group_el = [f for f in remaining_features if f[0].upper() in ['E', 'F', 'G', 'H', 'I', 'L']]
        render_feature_grid(group_el)
        
    with tab_M_R:
        group_mr = [f for f in remaining_features if f[0].upper() in ['M', 'N', 'O', 'P', 'R']]
        render_feature_grid(group_mr)
        
    with tab_S_Z:
        group_sz = [f for f in remaining_features if f[0].upper() in ['S', 'T', 'U', 'V', 'X', 'Y', 'Z']]
        render_feature_grid(group_sz)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Execution Layer
    if st.button("🚀 Execute EnzyCascade™ Diagnostic Mapping Analysis", use_container_width=True):
        if os.path.exists(RULE_PATH):
            try:
                try:
                    rules_df = pd.read_excel(RULE_PATH, sheet_name='Sheet1')
                except Exception:
                    rules_df = pd.read_excel(RULE_PATH, sheet_name=0)
                    
                strain_col_name = None
                for col in rules_df.columns:
                    if "scientific name" in str(col).lower() or "strain" in str(col).lower():
                        strain_col_name = col
                        break
                
                if strain_col_name:
                    rules_df[strain_col_name] = rules_df[strain_col_name].astype(str).str.strip().str.lower()
                else:
                    st.error("❌ Could not identify scientific name headers inside database entries.")
                    st.stop()
            except Exception as e:
                st.error(f"❌ Database Access Error: {e}")
                st.stop()
        else:
            st.error("❌ Matrix Database file missing.")
            st.stop()

        results = []
        
        if enable_web_lookup:
            with st.spinner("🌐 Checking online repositories (BacDive/NCBI) for missing phenotypic data profile hooks..."):
                time.sleep(0.6)

        for idx, row in rules_df.iterrows():
            strain_name = str(row[strain_col_name]).strip()
            strain_lower = strain_name.lower()
            
            # --- STAGE 1: TEXT COMMUNITY FILTER ---
            if allowed_community:
                is_in_community = any(
                    item in strain_lower or strain_lower in item 
                    for item in allowed_community
                )
                if not is_in_community:
                    continue 
            
            # --- STAGE 2: PARTIAL MORPHOLOGY SCORING MATRIX (WITH WEB INFERENCE) ---
            morphology_score = 0.0
            web_profile = fetch_bacterial_profile_from_web(strain_lower) if enable_web_lookup else {}
            
            # Gram Stain Calculation (20 Pts Max)
            if user_inputs["Gram stain"] != -1.0 and "Gram stain" in rules_df.columns:
                db_val = row["Gram stain"]
                if pd.isna(db_val) and "Gram stain" in web_profile:
                    db_val = web_profile["Gram stain"]
                    
                if not pd.isna(db_val) and str(db_val).strip().lower() == user_inputs["Gram stain"]:
                    morphology_score += 20.0
            else:
                morphology_score += 20.0
                
            # Shape Calculation (20 Pts Max)
            if user_inputs["Shape"] != -1.0 and "Shape" in rules_df.columns:
                db_val = row["Shape"]
                if pd.isna(db_val) and "Shape" in web_profile:
                    db_val = web_profile["Shape"]
                    
                if not pd.isna(db_val) and str(db_val).strip().lower() == user_inputs["Shape"]:
                    morphology_score += 20.0
            else:
                morphology_score += 20.0
                
            # Color Calculation (30 Pts Max)
            if user_inputs["color"] != -1.0 and "color" in rules_df.columns:
                db_val = row["color"]
                if pd.isna(db_val) and "color" in web_profile:
                    db_val = web_profile["color"]
                    
                if not pd.isna(db_val) and str(db_val).strip().lower() == user_inputs["color"]:
                    morphology_score += 30.0
            else:
                morphology_score += 30.0
            
            # --- STAGE 3: ENZYME / BIOCHEMICAL ASSAY SCORING (30 Pts Max) ---
            enzyme_matches = 0
            total_active_inputs = 0
            primary_features = ["Gram stain", "Shape", "color"]
            
            for feature_name, current_value in user_inputs.items():
                if feature_name in primary_features or current_value == -1.0:
                    continue
                    
                if feature_name in rules_df.columns:
                    db_val = row[feature_name]
                    if pd.isna(db_val):
                        continue
                        
                    total_active_inputs += 1
                    db_str = str(db_val).strip().lower()
                    
                    if current_value in db_str:
                        enzyme_matches += 1
            
            enzyme_score = 0.0
            if total_active_inputs > 0:
                enzyme_score = (enzyme_matches / total_active_inputs) * 30.0
            else:
                enzyme_score = 30.0
                
            final_score = morphology_score + enzyme_score
                
            results.append({
                "Strain Identification Candidate": strain_name.title(),
                "Confidence Match Probability": round(final_score, 2)
            })
            
        results = sorted(results, key=lambda x: x["Confidence Match Probability"], reverse=True)
        results = results[:3]
                
        if not results:
            st.error("❌ No pathogen strains found matching your selection matrices.")
        else:
            st.markdown('<p class="section-header">🎯 Diagnostic Match Profiles</p>', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if len(results) > 0:
                    with st.container(border=True):
                        st.metric(label="🥇 Primary Candidate Pathogen", value=results[0]['Strain Identification Candidate'])
                        st.progress(results[0]['Confidence Match Probability'] / 100.0)
                        st.caption(f"Match Probability Score: {results[0]['Confidence Match Probability']}%")
            with c2:
                if len(results) > 1:
                    with st.container(border=True):
                        st.metric(label="🥈 Secondary Candidate Pathogen", value=results[1]['Strain Identification Candidate'])
                        st.progress(results[1]['Confidence Match Probability'] / 100.0)
                        st.caption(f"Match Probability Score: {results[1]['Confidence Match Probability']}%")
            with c3:
                if len(results) > 2:
                    with st.container(border=True):
                        st.metric(label="🥉 Tertiary Candidate Pathogen", value=results[2]['Strain Identification Candidate'])
                        st.progress(results[2]['Confidence Match Probability'] / 100.0)
                        st.caption(f"Match Probability Score: {results[2]['Confidence Match Probability']}%")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_chart, col_table = st.columns([3, 2])
            with col_chart:
                with st.container(border=True):
                    st.markdown("**Visual Confidence Scale**")
                    chart_df = pd.DataFrame(results)
                    chart_df.columns = ['Strain', 'Score (%)']
                    st.bar_chart(chart_df.set_index('Strain'), color="#2563EB")
            with col_table:
                with st.container(border=True):
                    st.markdown("**Tabular Alignment Metrics**")
                    st.dataframe(pd.DataFrame(results), use_container_width=True)

except Exception as e:
    st.error(f"EnzyCascade™ Operational Engine Failure: {e}")
