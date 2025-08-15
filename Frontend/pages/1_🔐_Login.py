import os, requests, streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://web:8000")
st.set_page_config(page_title="Login", layout="centered")

# hide sidebar while on login
st.markdown("""
<style>
.css-18e3th9 {padding-top: 0rem;} /* tighten top padding */
[data-testid="stSidebar"] {display:none;}
</style>
""", unsafe_allow_html=True)

st.markdown("## IT AUDIT PLATFORM")

email = st.text_input("Email", value=st.session_state.get("email",""))
password = st.text_input("Password", type="password")

def do_login():
    try:
        r = requests.post(f"{BACKEND_URL}/auth/login",
                          json={"email": email, "password": password},
                          timeout=15)
        r.raise_for_status()
        token = r.json()["access_token"]
        st.session_state["token"] = token
        st.session_state["email"] = email
        st.success("You are logged in.")
        st.experimental_set_query_params()  # clear any params
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

if st.button("Login"):
    do_login()

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.button("Sign in with Google", disabled=True)
with col2:
    st.button("Sign in with Outlook", disabled=True)
st.link_button("Forgot password?", "#", disabled=True)

# auto-redirect to Home once token exists
if "token" in st.session_state:
    st.toast("Logged in", icon="✅")
    st.switch_page("Home.py")
