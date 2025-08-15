import streamlit as st
from common import render_primary_sidebar, require_auth

st.set_page_config(page_title="Home", layout="wide")

# gate: if not logged in, send to login page
if "token" not in st.session_state:
    st.switch_page("pages/1__🔐_Login.py")

render_primary_sidebar()

st.caption("You are logged in as: " + st.session_state.get("email", ""))
st.markdown("### Home")
st.write("Pick a project on the left, then use the secondary bar to open Tasks, Controls, or the Client Dashboard.")
