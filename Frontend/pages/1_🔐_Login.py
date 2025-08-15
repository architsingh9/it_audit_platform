import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("🔐 Login")

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
        st.success("Logged in.")
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

if st.button("Login"):
    do_login()

if "token" in st.session_state:
    st.info("Already logged in.")
