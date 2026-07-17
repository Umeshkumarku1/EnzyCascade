import streamlit as st
import pandas as pd
import os

# 1. Page Config
st.set_page_config(page_title="EnzyCascade™ | Diagnostic Portal", page_icon="🧬", layout="wide")

# 2. Database Loader (The "Gatekeeper")
DB_PATH = "phenotype_database-v2.xlsx"
COMMUNITY_TXT_PATH = "bacterial community.txt"

@st.cache_data
def load_db():
    if not os.path.exists(DB_PATH):
        return None
    try:
        return pd.read_excel(DB_PATH, sheet_name=0)
    except Exception:
        return None

def load_allowed_community():
    if os.path.exists(COMMUNITY_TXT_PATH):
        try:
            with open(COMMUNITY_TXT_PATH, 'r', encoding='utf-8') as f:
                return [line.strip().lower() for line in f.readlines() if line.strip()]
        except: return []
    return []

# Attempt to load immediately
df = load_db()
allowed_community = load_allowed_community()

# 3. Safe Rendering Gate
if df is None:
    st.error(f"⚠️ Critical Error: '{DB_PATH}' was not found in the root directory. Please upload the file to your GitHub repository.")
    st.stop() 

# 4. Main UI
st.markdown('<p style="font-size: 2.8rem; font-weight: 800; color: #1E3A8A;">EnzyCascade™</p>', unsafe_html=True)
st.markdown("---")

feature_list = [c for c in df.columns if "strain" not in c.lower() and "name" not in c.lower()]

st.sidebar.markdown("### 📊 Engine Status")
st.success("Database Loaded Successfully")

st.markdown("### 📋 Phase 1: Observed Laboratory Profiles")
user_inputs = {}
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

st.markdown("### 🧬 Phase 2: Enzyme Cascade Matrix")
remaining_features = [f for f in feature_list if f not in ["Gram stain", "Shape", "color"]]
cols = st.columns(4)
for i, feat in enumerate(remaining_features):
    with cols[i % 4]:
        val = st.selectbox(f"{feat}:", ["Not Performed", "Negative", "Variable", "Positive"], key=f"ui_{feat}")
        user_inputs[feat] = val.lower() if val != "Not Performed" else -1.0

if st.button("🚀 Execute EnzyCascade™ Mapping"):
    strain_col = [c for c in df.columns if "strain" in c.lower() or "name" in c.lower()][0]
    results = []
    
    for idx, row in df.iterrows():
        strain_name = str(row[strain_col]).lower()
        if allowed_community and not any(item in strain_name for item in allowed_community): continue
        
        score = 0.0
        for p in ["Gram stain", "Shape", "color"]:
            db_v = str(row.get(p, "")).lower() if not pd.isna(row.get(p)) else ""
            if user_inputs[p] != -1.0 and user_inputs[p] == db_v: score += 20.0 if p != "color" else 30.0
            elif user_inputs[p] == -1.0: score += 20.0 if p != "color" else 30.0
        
        e_match, e_total = 0, 0
        for f, v in user_inputs.items():
            if f not in ["Gram stain", "Shape", "color"] and v != -1.0:
                e_total += 1
                if str(row.get(f, "")).lower() == v: e_match += 1
        score += (e_match / e_total * 30.0) if e_total > 0 else 30.0
        results.append({"Strain": strain_name.title(), "Match_Percent": round(score, 2)})
        
    res = pd.DataFrame(results).sort_values("Match_Percent", ascending=False).head(3)
    res.columns = ["Strain", "Match (%)"]
    st.dataframe(res, use_container_width=True)
