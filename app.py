import streamlit as st
import pandas as pd
import os
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="EnzyCascade™ | Diagnostics", page_icon="🧬", layout="wide")

# 2. Modern Clinical Styling
st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; }
        h1 { color: #064E3B !important; font-weight: 900 !important; }
        .tagline { color: #0F766E !important; font-size: 1.2rem !important; font-style: italic; margin-bottom: 25px !important; }
        .stButton>button { width: 100%; border-radius: 10px; background-color: #059669 !important; color: white !important; font-weight: 700; }
        [data-testid="stMetricValue"] { color: #059669 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. Data Loading
DB_PATH = "phenotype_database-v2.xlsx"
@st.cache_data
def get_data():
    if not os.path.exists(DB_PATH): return None
    return pd.read_excel(DB_PATH, engine='openpyxl')

df = get_data()
if df is None:
    st.error("⚠️ Database missing.")
    st.stop()

# 4. Header
st.title("🧬 EnzyCascade™")
st.markdown('<p class="tagline">Biochemical Identification Engine</p>', unsafe_allow_html=True)

# 5. UI Inputs
with st.sidebar:
    st.header("⚙️ Assay Input Console")
    user_inputs = {}
    user_inputs["Gram stain"] = st.selectbox("Gram Stain", ["Not Performed", "Gram-negative", "Gram-positive"])
    user_inputs["Shape"] = st.selectbox("Morphology", ["Not Performed", "Rod", "Coccus", "Filamentous"])
    user_inputs["color"] = st.selectbox("Pigmentation", ["Not Performed", "white", "yellow", "gray", "green", "pink", "red"])
    
    features = [c for c in df.columns if c not in ["Gram stain", "Shape", "color", "strains.Full Scientific Name"]]
    for f in features:
        user_inputs[f] = st.selectbox(f"{f}", ["Not Performed", "Negative", "Variable", "Positive"])

# 6. Logic & Visualization
if st.button("🚀 EXECUTE MAPPING ANALYSIS"):
    results = []
    strain_col = [c for c in df.columns if "strain" in c.lower() or "name" in c.lower()][0]
    
    for _, row in df.iterrows():
        score = sum(10.0 for k, v in user_inputs.items() if v != "Not Performed" and str(row.get(k, "")).lower() == v.lower())
        results.append({"Strain": str(row[strain_col]), "Confidence": round(score, 2)})
    
    res = pd.DataFrame(results).sort_values("Confidence", ascending=False).head(5)
    
    # --- Professional Metric Display ---
    top = res.iloc[0]
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Top Candidate", top['Strain'])
    col_b.metric("Confidence Score", f"{top['Confidence']}%")
    col_c.metric("Assay Status", "Complete")
    
    st.markdown("---")
    
    # --- Energetic Visuals ---
    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(res, use_container_width=True, hide_index=True)
    with col2:
        fig = px.bar(res, x='Confidence', y='Strain', orientation='h',
                     color='Confidence', color_continuous_scale='Tealgrn',
                     text='Confidence')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
