import streamlit as st
from common import render_primary_sidebar, require_auth, secondary_bar_and_main, api_get

st.set_page_config(page_title="Client Dashboard", layout="wide")
require_auth()
render_primary_sidebar()

pid = st.session_state.get("selected_project_id")
body = secondary_bar_and_main("Client Dashboard")

if not pid:
    st.info("Select a project to view the dashboard.")
else:
    with body:
        st.write("Dashboard placeholder – will use controls/tasks for metrics.")
