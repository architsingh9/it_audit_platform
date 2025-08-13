import streamlit as st
import requests, os, pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
st.title("📦 Evidence")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}

# Choose control
try:
    controls = requests.get(f"{BACKEND_URL}/controls", headers=headers, timeout=20).json()
except Exception as e:
    st.error(f"Failed to get controls: {e}")
    st.stop()

cid = st.selectbox("Select Control", [f'{c["id"]} - {c["control_id_tag"]}' for c in controls] if controls else [])
control_id = int(cid.split(" - ")[0]) if cid else None

if control_id:
    st.subheader("Evidence Requests")
    try:
        reqs = requests.get(f"{BACKEND_URL}/controls/{control_id}/requests", headers=headers, timeout=20).json()
    except Exception as e:
        st.error(f"Failed to load requests: {e}")
        st.stop()

    if reqs:
        df = pd.DataFrame(reqs)
        st.dataframe(df[["id", "description", "status", "requested_by_id", "requested_at"]])
    else:
        st.info("No requests yet.")

    with st.expander("Create evidence request (Auditor L1+ / Admin)"):
        desc = st.text_input("Description")
        last_year = st.text_input("Last year info (optional)")
        if st.button("Create Request"):
            payload = {"control_id": control_id, "description": desc, "last_year_info": last_year or None}
            try:
                r = requests.post(f"{BACKEND_URL}/controls/requests", json=payload, headers=headers, timeout=30)
                r.raise_for_status()
                st.success("Created")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Create failed: {e}")

    st.subheader("Upload evidence to a request")
    request_ids = [r["id"] for r in reqs] if reqs else []
    rid = st.selectbox("Evidence Request", request_ids)
    file = st.file_uploader("File")
    desc = st.text_area("Description (optional)")
    if st.button("Upload") and rid and file:
        files = {"file": (file.name, file.getvalue())}
        data = {"description": desc}
        try:
            rr = requests.post(f"{BACKEND_URL}/evidence/upload/{rid}", files=files, data=data, headers=headers, timeout=60)
            rr.raise_for_status()
            st.success("Uploaded")
        except Exception as e:
            st.error(f"Upload failed: {e}")

    if request_ids:
        st.subheader("List uploaded evidence")
        rid2 = st.selectbox("Pick request to list", request_ids, key="listreq")
        try:
            items = requests.get(f"{BACKEND_URL}/evidence/{rid2}/list", headers=headers, timeout=30).json()
            if items:
                df2 = pd.DataFrame(items)
                st.dataframe(df2[["id","filename","version_number","uploaded_at","uploaded_by_id"]])
                dl_id = st.selectbox("Download evidence id", [x["id"] for x in items])
                if st.button("Download"):
                    url = f"{BACKEND_URL}/evidence/download/{dl_id}"
                    st.markdown(f"[Click to download]({url})")
            else:
                st.info("No evidence yet.")
        except Exception as e:
            st.error(f"List failed: {e}")
