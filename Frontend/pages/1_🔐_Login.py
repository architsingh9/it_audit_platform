import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("🔐 Login")

email = st.text_input("Email", value=st.session_state.get("email", ""))
password = st.text_input("Password", type="password")

if st.button("Login"):
    try:
        r = requests.post(f"{BACKEND_URL}/auth/login", params={"email": email, "password": password}, timeout=15)
        r.raise_for_status()
        token = r.json()["access_token"]
        st.session_state["token"] = token
        st.session_state["email"] = email
        st.success("Logged in.")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

if "token" in st.session_state:
    st.info("Already logged in.")
