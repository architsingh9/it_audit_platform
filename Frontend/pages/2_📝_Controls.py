import streamlit as st
import requests, os, pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
st.title("📝 Controls")

token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

headers = {"Authorization": f"Bearer {token}"}

# List controls
try:
    resp = requests.get(f"{BACKEND_URL}/controls", headers=headers, timeout=20)
    resp.raise_for_status()
    controls = resp.json()
except Exception as e:
    st.error(f"Failed to fetch controls: {e}")
    st.stop()

df = pd.DataFrame(controls)
if not df.empty:
    st.dataframe(df[["id","control_id_tag","name","control_type","audit_year","status","released_to_client"]])
else:
    st.info("No controls yet.")

with st.expander("Create new control"):
    name = st.text_input("Name")
    tag = st.text_input("Control Tag (e.g., ITGC-002)")
    year = st.number_input("Audit Year", min_value=2000, max_value=2100, value=2025)
    desc = st.text_area("Description")
    ctype = st.selectbox("Type", ["ITGC", "ITAC"])
    cat = st.text_input("Category (optional)")
    freq = st.selectbox("Frequency (optional)", ["", "Daily", "Weekly", "Monthly", "Quarterly", "Annually", "Ad-hoc"])
    owner_id = st.number_input("Owner User ID (Client, optional)", min_value=0, value=0)
    if st.button("Create Control"):
        payload = {
            "name": name, "control_id_tag": tag, "audit_year": year, "description": desc,
            "control_type": ctype, "category": cat or None, "frequency": freq or None,
            "owner_id": owner_id or None
        }
        try:
            r = requests.post(f"{BACKEND_URL}/controls", json=payload, headers=headers, timeout=30)
            r.raise_for_status()
            st.success("Control created.")
            st.rerun()
        except Exception as e:
            st.error(f"Create failed: {e}")

# Details / Update / PBC
st.subheader("Control details & actions")
cid = st.selectbox("Select control ID", [c["id"] for c in controls] if controls else [])
if cid:
    r = requests.get(f"{BACKEND_URL}/controls/{cid}", headers=headers)
    d = r.json()
    st.json(d)

    with st.form(key="update_control"):
        status_new = st.text_input("Status (optional)", value=d.get("status",""))
        bottlenecks = st.text_area("Bottlenecks", value=d.get("bottlenecks") or "")
        progress_notes = st.text_area("Progress notes", value=d.get("progress_notes") or "")
        final_report_text = st.text_area("Final report text", value=d.get("final_report_text") or "")
        released_to_client = st.checkbox("Released to client", value=d.get("released_to_client", False))
        submitted = st.form_submit_button("Update Control")
        if submitted:
            payload = {
                "status": status_new or None,
                "bottlenecks": bottlenecks,
                "progress_notes": progress_notes,
                "final_report_text": final_report_text,
                "released_to_client": released_to_client
            }
            try:
                rr = requests.put(f"{BACKEND_URL}/controls/{cid}", json=payload, headers=headers, timeout=30)
                rr.raise_for_status()
                st.success("Updated")
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {e}")

    st.markdown("**AI PBC (simulated)**")
    ctx = st.text_input("Audit context")
    if st.button("Generate PBC"):
        try:
            rr = requests.post(f"{BACKEND_URL}/controls/{cid}/generate_pbc_ai", data={"audit_context": ctx}, headers=headers, timeout=30)
            rr.raise_for_status()
            st.code(rr.json().get("generated_pbc",""), language="markdown")
        except Exception as e:
            st.error(f"AI call failed: {e}")
