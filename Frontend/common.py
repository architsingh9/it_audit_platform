import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def get_headers():
    tok = st.session_state.get("token")
    return {"Authorization": f"Bearer {tok}"} if tok else {}

def api_get(path, **kwargs):
    r = requests.get(f"{BACKEND_URL}{path}", headers=get_headers(), timeout=30, **kwargs)
    r.raise_for_status()
    return r.json()

def api_post(path, json=None, data=None, files=None, **kwargs):
    r = requests.post(f"{BACKEND_URL}{path}", headers=get_headers(), json=json, data=data, files=files, timeout=60, **kwargs)
    r.raise_for_status()
    return r.json() if r.content else {}

def api_put(path, json=None, **kwargs):
    r = requests.put(f"{BACKEND_URL}{path}", headers=get_headers(), json=json, timeout=60, **kwargs)
    r.raise_for_status()
    return r.json()

def require_login():
    if "token" not in st.session_state:
        st.warning("Please log in first.")
        st.stop()

def project_picker(sidebar_placeholder):
    try:
        projects = api_get("/projects")
    except Exception as e:
        sidebar_placeholder.error(f"Failed to load projects: {e}")
        return None, []
    options = []
    for p in projects:
        dot = "🟢" if p["is_active"] else "🔴"
        options.append(f'{dot}  {p["name"]}  (#{p["id"]})')
    current = st.session_state.get("current_project_display")
    choice = sidebar_placeholder.selectbox("Projects", options, index=options.index(current) if current in options else 0)
    st.session_state["current_project_display"] = choice
    project_id = int(choice.split("(#")[-1].rstrip(")"))
    return project_id, projects

def secondary_nav():
    # “second left bar” inside main area
    with st.container():
        col_nav, col_main = st.columns([0.20, 0.80], gap="small")
    return col_nav, col_main
