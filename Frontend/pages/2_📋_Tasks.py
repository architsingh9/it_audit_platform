import streamlit as st
import pandas as pd
from common import require_login, project_picker, api_get, api_post, api_put, secondary_nav

st.title("📋 Tasks")
require_login()

# Primary sidebar: Projects (+ compact toggle)
sb = st.sidebar
compact = sb.toggle("Compact project bar", value=True)
pid, projects = project_picker(sb)

# Secondary nav column
left, main = secondary_nav()
with left:
    st.header("Navigate")
    st.page_link("pages/2_📋_Tasks.py", label="Tasks", icon="📋")
    st.page_link("pages/3_📝_Controls.py", label="Controls", icon="📝")
    st.page_link("pages/5_📊_Client_Dashboard.py", label="Client Dashboard", icon="📊")

with main:
    # Top mini dashboard
    try:
        controls = api_get(f"/controls?project_id={pid}")
        tasks = api_get(f"/tasks?project_id={pid}")
    except Exception as e:
        st.error(f"Load failed: {e}")
        st.stop()

    in_progress = sum(1 for c in controls if "Progress" in c["status"])
    pending_client = sum(1 for c in controls if c["status"] == "Evidence Requested")
    with_bottlenecks = sum(1 for c in controls if (c.get("bottlenecks") or "").strip())

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Controls in Progress", in_progress)
    c2.metric("Controls Pending Client Action", pending_client)
    c3.metric("Controls with Bottlenecks", with_bottlenecks)

    st.subheader("To-Do List")
    df = pd.DataFrame(tasks) if tasks else pd.DataFrame(columns=[
        "id","description","priority","status","start_date","end_date","notes","assigned_to_id","control_id"
    ])
    # turn into S.No
    if not df.empty:
        df.insert(0, "S.No", range(1, len(df)+1))
        st.dataframe(df[["S.No","description","priority","status","start_date","end_date","notes","assigned_to_id","control_id"]], use_container_width=True)
    else:
        st.info("No tasks yet for this project.")

    st.markdown("**Create task**")
    desc = st.text_input("Description")
    prio = st.selectbox("Priority", ["High","Medium","Low"])
    stat = st.selectbox("Status", ["Todo","In Progress","Blocked","Done"], index=0)
    sd = st.text_input("Start Date (YYYY-MM-DD)", "")
    ed = st.text_input("End Date (YYYY-MM-DD)", "")
    notes = st.text_area("Notes")
    ctrl_id = st.number_input("Link to Control ID (optional)", min_value=0, value=0)

    if st.button("Add Task"):
        try:
            payload = {
                "project_id": pid,
                "control_id": int(ctrl_id) or None,
                "description": desc, "priority": prio, "status": stat,
                "start_date": sd or None, "end_date": ed or None, "notes": notes or None
            }
            api_post("/tasks", json=payload)
            st.success("Task created")
            st.rerun()
        except Exception as e:
            st.error(f"Create failed: {e}")
