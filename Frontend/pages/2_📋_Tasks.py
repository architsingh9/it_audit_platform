import streamlit as st
from common import render_primary_sidebar, require_auth, secondary_bar_and_main, api_get

st.set_page_config(page_title="Tasks", layout="wide")
require_auth()
render_primary_sidebar()

project_id = st.session_state.get("selected_project_id")
body = secondary_bar_and_main("Tasks")

if not project_id:
    st.info("Select a project on the left to see its tasks.")
else:
    try:
        tasks = api_get("/tasks/", params={"project_id": project_id})
    except Exception as e:
        st.error(f"Load failed: {e}")
        tasks = []

    with body:
        st.markdown("#### My Task List")
        if tasks:
            import pandas as pd
            df = pd.DataFrame(tasks)[["id","description","priority","status","start_date","end_date","notes","control_id","assigned_to_id"]]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.write("No tasks yet for this project.")
