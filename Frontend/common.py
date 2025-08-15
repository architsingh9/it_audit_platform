import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://web:8000")

# ---- session helpers ----
def require_auth():
    if "token" not in st.session_state:
        st.switch_page("pages/1__🔐_Login.py")  # hard redirect
    return st.session_state.get("token")

def api_get(path, params=None):
    token = st.session_state.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.get(f"{BACKEND_URL}{path}", params=params or {}, headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()

# ---- primary sidebar: Home + Projects ----
def render_primary_sidebar():
    with st.sidebar:
        st.header("Home")
        st.page_link("Home.py", label="🏠 Home")

        st.markdown("---")
        st.subheader("Projects")

        # preload projects
        if "projects_cache" not in st.session_state:
            try:
                st.session_state["projects_cache"] = api_get("/projects")
            except Exception:
                st.session_state["projects_cache"] = []

        projs = st.session_state["projects_cache"]
        labels = [f'{"🟢" if p["is_active"] else "🔴"} {p["name"]} (#{p["id"]})' for p in projs]
        ids = [p["id"] for p in projs]

        current = st.session_state.get("selected_project_id")
        default_index = ids.index(current) if current in ids else (0 if ids else None)

        sel = st.selectbox("Select project", options=ids, index=default_index if default_index is not None else None,
                           format_func=lambda pid: labels[ids.index(pid)] if pid in ids else "—")
        if sel:
            st.session_state["selected_project_id"] = sel

        st.toggle("Compact project bar", key="compact_project_bar", value=True, help="Toggle secondary bar width")

# ---- secondary bar: appears inside pages when a project is selected ----
def secondary_bar_and_main(title: str):
    selected = st.session_state.get("selected_project_id")
    if not selected:
        # single full-width column if no project yet
        return st.container()

    # width ratio
    narrow = 0.18 if not st.session_state.get("compact_project_bar", True) else 0.13
    left, right = st.columns([narrow, 1 - narrow], gap="small")

    with left:
        st.markdown("### Navigate")
        st.page_link("pages/2__📋_Tasks.py", label="📋 Tasks")
        st.page_link("pages/3__📝_Controls.py", label="📝 Controls")
        st.page_link("pages/5__📊_Client_Dashboard.py", label="📊 Client Dashboard")

    with right:
        st.markdown(f"## {title}")
        return right
