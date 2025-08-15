import streamlit as st
from common import render_primary_sidebar, require_auth, secondary_bar_and_main, api_get

st.set_page_config(page_title="Controls", layout="wide")
require_auth()
render_primary_sidebar()

project_id = st.session_state.get("selected_project_id")
body = secondary_bar_and_main("Controls")

if not project_id:
    st.info("Select a project on the left to see its controls.")
else:
    q = st.text_input("Search (control_id_tag / name)", key="controls_q")
    params = {"project_id": project_id}
    if q: params["q"] = q

    try:
        controls = api_get("/controls/", params=params)
    except Exception as e:
        st.error(f"Load failed: {e}")
        controls = []

    with body:
        if not controls:
            st.write("No controls found.")
        else:
            import json
            # simple list with quick JSON preview (placeholder for your blue/yellow/pink layout work)
            ids = [f'{c["id"]} – {c["control_id_tag"]}: {c["name"]}' for c in controls]
            idx = st.selectbox("Select control", range(len(controls)), format_func=lambda i: ids[i])
            st.code(json.dumps(controls[idx], indent=2))
