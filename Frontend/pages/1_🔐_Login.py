import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- Page setup ---
st.set_page_config(page_title="Login • AI IT Audit Platform", page_icon="🔐", layout="centered")

# Hide the sidebar ONLY on this page; keep it on others
st.markdown(
    """
    <style>
      [data-testid="stSidebar"] { display: none; }      /* hide sidebar */
      header { visibility: hidden; }                    /* hide top hamburger */
      .block-container { max-width: 720px; padding-top: 3rem; }
      .auth-buttons .stButton>button { width: 100%; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align:center'>🤖 AI IT AUDIT PLATFORM</h1>", unsafe_allow_html=True)
st.divider()

# --- Login form ---
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

col_login, _ = st.columns([1, 2])
with col_login:
    if st.button("Login"):
        do_login()

st.markdown("### ")  # a little vertical space

# --- Social buttons (placeholders for now) ---
st.markdown("##### Or")
with st.container():
    st.markdown('<div class="auth-buttons">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔵 Sign in with Google"):
            st.info("Google sign-in not configured yet.")
    with c2:
        if st.button("🔵 Sign in with Outlook"):
            st.info("Outlook sign-in not configured yet.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Forgot password ---
st.markdown("")
if st.link_button("Forgot password?", "#"):
    st.info("Password reset isn’t configured yet. Use your demo credentials for now.")

# Already logged in?
if "token" in st.session_state:
    st.info("Already logged in.")
