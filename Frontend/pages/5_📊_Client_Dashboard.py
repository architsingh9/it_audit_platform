import streamlit as st
import requests, os, pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
st.title("📊 Client Dashboard")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}

try:
    items = requests.get(f"{BACKEND_URL}/client_dashboard", headers=headers, timeout=30).json()
    if items:
        df = pd.DataFrame(items)
        cols = ["id","control_id_tag","name","status","released_to_client","progress_notes","bottlenecks","final_report_text"]
        show = [c for c in cols if c in df.columns]
        st.dataframe(df[show])
    else:
        st.info("No controls to show.")
except Exception as e:
    st.error(f"Load failed: {e}")
