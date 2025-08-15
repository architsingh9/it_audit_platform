import streamlit as st
import requests, os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("🤖 AI IT AUDIT PLATFORM")

st.write("")
c1, c2, c3 = st.columns([1,1,1])
with c1:
    if st.button("🔵  Sign in with Google"):
        st.info("Google SSO not configured in this prototype.")
with c2:
    if st.button("🟦  Sign in with Outlook"):
        st.info("Outlook SSO not configured in this prototype.")
with c3:
    st.markdown("<div style='text-align:right;'><a href='#'>Forgot password?</a></div>", unsafe_allow_html=True)

st.write("---")

email = st.text_input("Email", value=st.session_state.get("email", ""))
password = st.text_input("Password", type="password")

def do_login():
    try:
        r = requests.post(f"{BACKEND_URL}/auth/login", json={"email": email, "password": password}, timeout=15)
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
