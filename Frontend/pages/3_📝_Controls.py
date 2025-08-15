import streamlit as st
import pandas as pd
from common import require_login, project_picker, api_get, api_post, api_put, secondary_nav

st.title("📝 Controls")
require_login()

# Main sidebar: Projects + toggle
sb = st.sidebar
compact = sb.toggle("Compact project bar", value=True)
pid, projects = project_picker(sb)

# Secondary bar (inside page)
left, main = secondary_nav()
with left:
    st.header("Navigate")
    st.page_link("pages/2_📋_Tasks.py", label="Tasks", icon="📋")
    st.page_link("pages/3_📝_Controls.py", label="Controls", icon="📝")
    st.page_link("pages/5_📊_Client_Dashboard.py", label="Client Dashboard", icon="📊")

with main:
    # Green bar – search
    st.text_input("control_id_tag    name", key="ctrl_search", placeholder="Type to search…")

    # Load controls for project
    q = st.session_state.get("ctrl_search") or ""
    try:
        controls = api_get(f"/controls?project_id={pid}&q={q}") if pid else api_get("/controls")
    except Exception as e:
        st.error(f"Load failed: {e}")
        st.stop()

    # Red bars – list of risks
    if not controls:
        st.info("No controls yet for this project.")
        st.stop()

    # simple pick
    cid = st.selectbox("Select control ID", [c["id"] for c in controls])
    current = next(c for c in controls if c["id"] == cid)
    st.code(current, language="json")

    # Blue box – detailed description + Grey dropdown for ITGC/ITAC
    st.markdown("### Control Overview")
    cA, cB = st.columns([0.75, 0.25])
    with cA:
        st.info(current.get("description") or "No description")
    with cB:
        new_type = st.selectbox("Type", ["ITGC","ITAC"], index=0 if current["control_type"]=="ITGC" else 1)
        if new_type != current["control_type"]:
            try:
                api_put(f"/controls/{cid}", json={"control_type": new_type})
                st.success("Type updated")
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {e}")

    # Yellow box – documents/evidence/ERL with 3 checks + upload date
    st.markdown("### Evidence & Documents")
    try:
        reqs = api_get(f"/controls/{cid}/requests")
    except Exception as e:
        st.error(f"Failed to load requests: {e}")
        reqs = []

    if reqs:
        tbl = []
        for r in reqs:
            # naive rollups (in real app: join with approvals)
            provided = "✅" if r["status"] == "provided" else "⏳"
            l1 = "✅" if "L1" in current["status"] else "☐"
            l2 = "✅" if "L2" in current["status"] else "☐"
            l3 = "✅" if "L3" in current["status"] or "L4" in current["status"] else "☐"
            tbl.append({
                "ERL / Evidence Request": r["description"],
                "Client Upload Status": provided,
                "Upload Date": r["updated_at"][:10],
                "L1": l1, "L2": l2, "L3": l3
            })
        st.dataframe(pd.DataFrame(tbl), use_container_width=True)
    else:
        st.info("No ERLs yet for this control.")

    with st.expander("Create ERL / Evidence Request"):
        desc = st.text_input("Description")
        last_year = st.text_input("Last year info (optional)")
        if st.button("Create ERL"):
            try:
                api_post("/controls/requests", json={"control_id": cid, "description": desc, "last_year_info": last_year or None})
                st.success("ERL created")
                st.rerun()
            except Exception as e:
                st.error(f"Create failed: {e}")

    # Pink box – AI Notes placeholder
    st.markdown("### 🤖 AI Notes")
    st.caption("This is a placeholder where the LLM will summarize transcripts, draft MOM, and pre-fill notes.")
    st.text_area("Draft notes (auto-generated later)", value=current.get("progress_notes") or "", height=150)
