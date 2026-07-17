import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(
    page_title="EnzyCascade™ | Biotech Diagnostics", 
    page_icon="🧬", 
    layout="wide"
)

# 2. Vibrant Bio-Clinical Styling
st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; }
        h1 { color: #064E3B !important; font-weight: 900 !important; }
        .tagline { color: #0F766E !important; font-size: 1.3rem !important; font-style: italic; margin-bottom: 30px !important; }
        .stButton>button { 
            width: 100%; border-radius: 12px; background-color: #059669 !important; 
            color: white !important; font-weight: 700; padding: 12px; border: none; 
            box-shadow: 0 4px 6px -1px rgba(5, 150, 105, 0.3);
        }
        .stSelectbox>div>div { background-color: #F0FDFA !important; border: 1px solid #A7F3D0 !important; }
        [data-testid="stDataFrame"] { border: 1px solid #D1FAE5; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 3. Data Loading Gatekeeper
DB_PATH = "phenotype_database-v2.xlsx"

@st.cache_data
def get_data():
    if not os.path.exists(DB_PATH): return None
    try: return pd.read_excel(DB_PATH, engine='openpyxl')
    except: return None

df = get_data()
if df is None:
    st.error("⚠️ Database 'phenotype_database-v2.xlsx' not found. Please upload to the root directory.")
    st.stop()

# 4. Header Section
st.title("🧬 EnzyCascade™")
st.markdown('<p class="tagline">Rule-Based Enzyme Cascade Bacterial Identification System</p>', unsafe_allow_html=True)

# 5. UI Layout: Morphology Inputs
st.subheader("📋 Primary Morphology")
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    user_inputs = {}
    with col1:
        user_inputs["Gram stain"] = st.selectbox("Gram Stain", ["Not Performed", "Gram-negative", "Gram-positive"])
    with col2:
        user_inputs["Shape"] = st.selectbox("Morphology", ["Not Performed", "Rod", "Coccus", "Filamentous"])
    with col3:
        user_inputs["color"] = st.selectbox("Pigmentation", ["Not Performed", "white", "yellow", "gray", "green", "pink", "red"])

# 6. UI Layout: Secondary Assays
st.subheader("🧪 Secondary Cascade Assays")
features = [c for c in df.columns if c not in ["Gram stain", "Shape", "color", "strains.Full Scientific Name"]]
with st.container(border=True):
    cols = st.columns(4)
    for i, f in enumerate(features):
        user_inputs[f] = cols[i % 4].selectbox(f"{f}", ["Not Performed", "Negative", "Variable", "Positive"])

# 7. Logic Engine
if st.button("🚀 INITIATE MICROBIAL MAPPING"):
    results = []
    strain_col = [c for c in df.columns if "strain" in c.lower() or "name" in c.lower()][0]
    
    for _, row in df.iterrows():
        score = 0.0
        # Calculate matching score based on user input vs database
        for k, v in user_inputs.items():
            if v != "Not Performed":
                db_val = str(row.get(k, "")).lower()
                if db_val == v.lower():
                    score += 10.0
        
        results.append({"Candidate Strain": str(row[strain_col]), "Confidence Score": round(score, 2)})
    
    # Sort by confidence
    res = pd.DataFrame(results).sort_values("Confidence Score", ascending=False).head(5)
    
    st.markdown("---")
    st.success("✅ Analysis Complete. Top-ranked identification candidates:")
    st.dataframe(res, use_container_width=True, hide_index=True)
