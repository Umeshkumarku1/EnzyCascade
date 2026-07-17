import streamlit as st
import pandas as pd
import os

# 1. Page Config
st.set_page_config(page_title="EnzyCascade™ | AI Engine", page_icon="🧬", layout="wide")

# 2. Modern CSS Injection
st.markdown("""
    <style>
        .stApp { background-color: #0F172A; color: #F1F5F9; }
        .metric-card { background-color: #1E293B; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
        .stSelectbox>div>div { background-color: #1E293B !important; color: white !important; }
        h1, h2, h3 { color: #38BDF8 !important; }
        .stButton>button { width: 100%; border-radius: 8px; background: linear-gradient(90deg, #0284C7, #38BDF8); color: white; border: none; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 3. Data Loading
DB_PATH = "phenotype_database-v2.xlsx"

@st.cache_data
def get_data():
    if not os.path.exists(DB_PATH): return None
    try: return pd.read_excel(DB_PATH, engine='openpyxl')
    except: return None

df = get_data()
if df is None:
    st.error("⚠️ Database file not detected.")
    st.stop()

# 4. UI Rendering
st.title("🧬 EnzyCascade™ Intelligence Engine")
st.markdown("### Microbial Identification & Genomic Analysis Dashboard")
st.write("---")

# Layout: Sidebar for Status
with st.sidebar:
    st.header("⚙️ System Status")
    st.metric("Database Entries", len(df))
    st.success("Engine: Operational")
    st.info("Environment: Secure Cluster")

# Input Sections in Professional Containers
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Primary Morphology")
    with st.container(border=True):
        user_inputs = {}
        user_inputs["Gram stain"] = st.selectbox("Gram Stain", ["Not Performed", "Gram-negative", "Gram-positive"])
        user_inputs["Shape"] = st.selectbox("Morphology", ["Not Performed", "Rod", "Coccus", "Filamentous"])
        user_inputs["color"] = st.selectbox("Pigmentation", ["Not Performed", "white", "yellow", "gray", "green", "pink", "red"])

with col2:
    st.subheader("🧪 Enzyme Cascade Matrix")
    features = [c for c in df.columns if c not in ["Gram stain", "Shape", "color", "strains.Full Scientific Name"]]
    with st.container(border=True):
        cols = st.columns(2)
        for i, f in enumerate(features):
            user_inputs[f] = cols[i % 2].selectbox(f"{f}", ["Not Performed", "Negative", "Variable", "Positive"])

# Execution
if st.button("🚀 EXECUTE MAPPING ANALYSIS"):
    # Convert inputs to numerical/clean values
    clean_inputs = {k: (v.lower() if v != "Not Performed" else -1.0) for k, v in user_inputs.items()}
    
    results = []
    strain_col = [c for c in df.columns if "strain" in c.lower() or "name" in c.lower()][0]
    
    for _, row in df.iterrows():
        score = 0.0
        # Simple scoring for demo
        for k, v in clean_inputs.items():
            if v != -1.0 and str(row.get(k, "")).lower() == v:
                score += 10.0
        results.append({"Candidate Strain": str(row[strain_col]), "Confidence Score": round(score, 2)})
    
    # Sort and Display
    res = pd.DataFrame(results).sort_values("Confidence Score", ascending=False).head(5)
    
    st.markdown("### 🎯 Diagnostic Results")
    st.dataframe(res, use_container_width=True, hide_index=True)
