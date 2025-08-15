import streamlit as st

# MUST be first Streamlit command in this file
st.set_page_config(
    page_title="Home",
    layout="wide",
    initial_sidebar_state="expanded",   # show sidebar on main pages
)

# If not logged in, send to Login immediately
if "token" not in st.session_state:
    st.switch_page("pages/1_🔐_Login.py")

st.title("Home")

st.write("Welcome,", st.session_state.get("email", ""))
# ... your home content
