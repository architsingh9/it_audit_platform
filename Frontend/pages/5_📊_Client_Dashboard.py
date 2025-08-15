import streamlit as st
import pandas as pd
from collections import Counter
from common import require_login, project_picker, api_get, secondary_nav

st.title("📊 Client Dashboard")
require_login()

sb = st.sidebar
compact = sb.toggle("Compact project bar", value=True)
pid, projects = project_picker(sb)

left, main = secondary_nav()
with left:
    st.header("Navigate")
    st.page_link("pages/2_📋_Tasks.py", label="Tasks", icon="📋")
    st.page_link("pages/3_📝_Controls.py", label="Controls", icon="📝")
    st.page_link("pages/5_📊_Client_Dashboard.py", label="Client Dashboard", icon="📊")

with main:
    try:
        items = api_get(f"/client_dashboard")  # server-side masks client visibility
        controls = [c for c in items if (not pid or c.get("project_id")==pid) or True]
    except Exception as e:
        st.error(f"Load failed: {e}")
        st.stop()

    # Executive Summary Metrics
    in_progress = sum(1 for c in controls if "Progress" in c["status"])
    pending_client = sum(1 for c in controls if c["status"] == "Evidence Requested")
    with_bottlenecks = sum(1 for c in controls if (c.get("bottlenecks") or "").strip())

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Controls in Progress", in_progress)
    m2.metric("Controls Pending Client Action", pending_client)
    m3.metric("Controls with Bottlenecks", with_bottlenecks)

    # Top Bottlenecks (simple keyword tokenization)
    text = " ".join((c.get("bottlenecks") or "").lower() for c in controls)
    vocab = ["pending", "client", "feedback", "data", "access", "issues", "approvals", "awaiting", "senior"]
    counts = Counter(w for w in text.split() if w in vocab)
    if counts:
        st.subheader("Top Bottlenecks")
        st.bar_chart(pd.DataFrame({"count": counts}).sort_values("count", ascending=False))
        st.dataframe(pd.DataFrame({"Bottleneck Category": list(counts.keys()), "Count of Controls": list(counts.values())}))
    else:
        st.info("No bottlenecks recorded yet.")

    # Detailed table (existing)
    st.subheader("Detailed Control Status")
    df = pd.DataFrame(controls) if controls else pd.DataFrame()
    if not df.empty:
        show = [c for c in ["id","project_id","control_id_tag","name","status","released_to_client","progress_notes","bottlenecks","final_report_text"] if c in df.columns]
        st.dataframe(df[show], use_container_width=True)
    else:
        st.info("No controls to show.")
