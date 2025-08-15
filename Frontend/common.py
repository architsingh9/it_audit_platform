# Frontend/common.py (add this helper)
import streamlit as st

def project_and_section_nav():
    # LEFT most: project selector (use your existing control)
    project_id = st.session_state.get("project_id")

    # SECOND rail: appears only when a project is selected
    with st.sidebar:
        st.markdown("---")
        if project_id:
            st.caption(f"Project #{project_id}")
            choice = st.radio(
                "Navigate",
                ["Tasks", "Controls", "Client Dashboard"],
                index=["Tasks", "Controls", "Client Dashboard"].index(
                    st.session_state.get("active_section", "Tasks")
                ),
                label_visibility="collapsed",
            )
            st.session_state["active_section"] = choice
            # Optional: programmatic navigation
            if choice == "Tasks":
                st.switch_page("pages/2__🗒️_Tasks.py")
            elif choice == "Controls":
                st.switch_page("pages/3__📝_Controls.py")
            else:
                st.switch_page("pages/5__📊_Client_Dashboard.py")
