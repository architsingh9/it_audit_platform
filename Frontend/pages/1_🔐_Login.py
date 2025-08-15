import os, requests, streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://web:8000")

st.set_page_config(page_title="Login", layout="wide")
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 14px !important; background: white; color: black; }
</style>
""", unsafe_allow_html=True)

st.title("IT AUDIT PLATFORM")

email = st.text_input("Email", "")
password = st.text_input("Password", type="password")

if st.button("Login"):
    try:
        r = requests.post(f"{BACKEND_URL}/auth/login",
                          json={"email": email, "password": password}, timeout=10)
        r.raise_for_status()
        st.session_state["token"] = r.json()["access_token"]
        st.session_state["email"] = email
        st.success("Login successful!")
        st.switch_page("pages/2_Home.py")
    except Exception as e:
        st.error(f"Login failed: {e}")
