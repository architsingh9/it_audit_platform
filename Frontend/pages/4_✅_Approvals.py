import streamlit as st
import requests, os, pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
st.title("✅ Approvals")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}

st.subheader("Create approval request (Control)")
doc_id = st.number_input("Control ID", min_value=1, value=1)
comment = st.text_input("Comments", value="Please review")
if st.button("Create Approval"):
    payload = {"document_type": "Control", "document_id": int(doc_id), "comments": comment}
    try:
        r = requests.post(f"{BACKEND_URL}/approvals", json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        st.success("Approval request created")
    except Exception as e:
        st.error(f"Create failed: {e}")

st.subheader("Pending / Relevant approvals")
try:
    items = requests.get(f"{BACKEND_URL}/approvals", headers=headers, timeout=30).json()
    if items:
        df = pd.DataFrame(items)
        st.dataframe(df[["id","document_type","document_id","status","current_level","approval_date"]])
        aid = st.selectbox("Choose approval id", [i["id"] for i in items])
        action = st.selectbox("Action", ["approve","reject","request_revisions","resubmit","release_to_client"])
        comments = st.text_input("Comments (required for reject/revisions)")
        if st.button("Perform Action"):
            payload = {"action": action, "comments": comments}
            try:
                rr = requests.post(f"{BACKEND_URL}/approvals/{aid}/action", json=payload, headers=headers, timeout=30)
                rr.raise_for_status()
                st.success("Action done")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Action failed: {e}")
    else:
        st.info("No approvals in your queue.")
except Exception as e:
    st.error(f"List failed: {e}")
