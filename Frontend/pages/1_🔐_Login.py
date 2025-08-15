import time
import os
import requests
import streamlit as st

# MUST be first Streamlit command in this file
st.set_page_config(
    page_title="AI IT AUDIT PLATFORM",
    layout="centered",
    initial_sidebar_state="collapsed",  # hide sidebar on login
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://web:8000")

st.title("AI IT AUDIT PLATFORM")
st.divider()

email = st.text_input("Email", value=st.session_state.get("email", ""))
password = st.text_input("Password", type="password")

def do_login():
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=15,
        )
        r.raise_for_status()
        token = r.json()["access_token"]
        st.session_state["token"] = token
        st.session_state["email"] = email
        st.success("You are logged in.")
        time.sleep(1)              # brief message then jump to Home
        st.switch_page("Home.py")
    except Exception as e:
        st.error(f"Login failed: {e}")

if st.button("Login"):
    do_login()

st.markdown("### Or")
col1, col2 = st.columns(2)
with col1:
    st.button("Sign in with Google", use_container_width=False)
with col2:
    st.button("Sign in with Outlook", use_container_width=False)

st.link_button("Forgot password?", "#", type="secondary")

# If already logged in, jump to Home directly
if "token" in st.session_state:
    st.info("Already logged in.")
    time.sleep(0.6)
    st.switch_page("Home.py")
