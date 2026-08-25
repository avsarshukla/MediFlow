import streamlit as st
import qrcode
from io import BytesIO
import json
import time
from datetime import datetime

# ---------- PREMADE 60‑YEAR‑OLD PROFILE ----------
PREMATURE = {
    "name": "Ramesh Sharma",
    "dob": "1966-03-15",                    # ~60 years
    "blood_group": "O+",
    "chief_complaint": "Acute substernal chest pain radiating to left arm",
    "duration": "45 minutes",
    "site": "Substernal",
    "onset": "Acute while walking",
    "character": "Squeezing / Heavy",
    "associated": "Diaphoresis, Shortness of breath",
    "severity": 8,
    "diabetes": "Type 2",
    "allergies": ["Environmental/Dust", "Medication"],   # includes dust and penicillin
    "past_history": "Hypertension (10 yrs), Type 2 Diabetes (8 yrs)",
    "medications": "Metformin 500mg BD, Amlodipine 5mg OD",
    "family_history": "Father: Hypertension",
    "tobacco": "Never",
    "alcohol": "Occasional",
    "ros_general": "Fatigue",
    "ros_cardio": "Chest tightness"
}

# ---------- SESSION STATE ----------
if "form_data" not in st.session_state:
    # Pre‑fill with the premade data for quick demo
    st.session_state.form_data = {
        "name": PREMATURE["name"],
        "dob": PREMATURE["dob"],
        "blood_group": PREMATURE["blood_group"],
        "chief_complaint": PREMATURE["chief_complaint"],
        "duration": PREMATURE["duration"],
        "site": PREMATURE["site"],
        "onset": PREMATURE["onset"],
        "character": PREMATURE["character"],
        "associated": PREMATURE["associated"],
        "severity": PREMATURE["severity"],
        "diabetes": PREMATURE["diabetes"],
        "allergies": PREMATURE["allergies"],
    }

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="MediKiosk Demo", layout="wide")
st.title("🏥 MediKiosk – Allopathy Dual‑Tier Demo")

# ---------- HELPER: compute age from DOB ----------
def get_age(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except:
        return None

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["📋 Patient Intake (10 Questions)", "🆘 Emergency QR", "👨‍⚕️ Doctor Dashboard"])

# ============================================================
# TAB 1: PATIENT INTAKE
# ============================================================
with tab1:
    st.header("Patient Intake – 10 Key Questions")
    st.caption("Fields are pre‑filled with the demo 60‑year‑old profile. Edit as needed.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Demographics")
        # Q1
        name = st.text_input("**1. Full Name**", value=st.session_state.form_data["name"])
        # Q2
        dob = st.date_input("**2. Date of Birth**", value=datetime.strptime(st.session_state.form_data["dob"], "%Y-%m-%d"))
        # Q3
        blood_group = st.selectbox(
            "**3. Blood Group**",
            ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"],
            index=["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"].index(st.session_state.form_data["blood_group"])
        )
        # Q4
        chief_complaint = st.text_area("**4. Primary Visit Reason**", value=st.session_state.form_data["chief_complaint"], height=70)
        # Q5
        duration = st.text_input("**5. Symptom Duration**", value=st.session_state.form_data["duration"])

        st.subheader("Additional Clinical Data (for QR & Dashboard)")
        # Diabetes – with options
        diabetes = st.selectbox(
            "**Diabetes status**",
            ["No", "Type 1", "Type 2", "Gestational", "Pre‑diabetes"],
            index=["No","Type 1","Type 2","Gestational","Pre‑diabetes"].index(st.session_state.form_data["diabetes"])
        )
        # Allergies – multiselect with common options
        allergy_options = ["Environmental/Dust", "Nuts/Food", "Medication", "Latex", "Other"]
        allergies = st.multiselect(
            "**Allergies (check all that apply)**",
            allergy_options,
            default=[a for a in st.session_state.form_data["allergies"] if a in allergy_options]
        )
        # If "Other" is selected, allow free text
        other_allergy = ""
        if "Other" in allergies:
            other_allergy = st.text_input("Please specify other allergies")
        # Combine selected + other
        if other_allergy:
            allergies = [a for a in allergies if a != "Other"] + [other_allergy]
        else:
            allergies = [a for a in allergies if a != "Other"]

    with col2:
        st.subheader("History of Presenting Illness (HPI)")
        # Q6
        site = st.text_input("**6. Site / Location**", value=st.session_state.form_data["site"])
        # Q7
        onset = st.text_input("**7. Onset Type**", value=st.session_state.form_data["onset"])
        # Q8
        character = st.text_input("**8. Symptom Character**", value=st.session_state.form_data["character"])
        # Q9
        associated = st.text_input("**9. Associated Symptoms**", value=st.session_state.form_data["associated"])
        # Q10
        severity = st.slider("**10. Severity Scale (0–10)**", 0, 10, value=st.session_state.form_data["severity"])

    # Update session state with all inputs
    st.session_state.form_data.update({
        "name": name,
        "dob": dob.strftime("%Y-%m-%d"),
        "blood_group": blood_group,
        "chief_complaint": chief_complaint,
        "duration": duration,
        "site": site,
        "onset": onset,
        "character": character,
        "associated": associated,
        "severity": severity,
        "diabetes": diabetes,
        "allergies": allergies,
    })

    # ---- SIMULATED VOICE ----
    if st.button("🎤 Simulate Voice Intake", use_container_width=True):
        with st.spinner("Processing voice input..."):
            time.sleep(1.5)
            st.session_state.form_data.update({
                "chief_complaint": PREMATURE["chief_complaint"],
                "duration": PREMATURE["duration"],
                "site": PREMATURE["site"],
                "onset": PREMATURE["onset"],
                "character": PREMATURE["character"],
                "associated": PREMATURE["associated"],
                "severity": PREMATURE["severity"],
                "diabetes": PREMATURE["diabetes"],
                "allergies": PREMATURE["allergies"],
            })
        st.success("Voice intake simulated! Fields updated.")
        st.rerun()

    # ---- SIMULATED OCR ----
    uploaded_file = st.file_uploader("📄 Upload Prescription (OCR Simulator)", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file is not None:
        with st.status("Simulating OCR parsing...", expanded=True) as status:
            st.write("Analyzing document...")
            time.sleep(0.8)
            st.write("Extracting text...")
            time.sleep(0.8)
            st.write("Identifying diabetes & allergies...")
            time.sleep(0.8)
            st.session_state.form_data.update({
                "diabetes": PREMATURE["diabetes"],
                "allergies": PREMATURE["allergies"],
            })
            status.update(label="OCR complete!", state="complete")
        st.success("Prescription parsed! Diabetes & allergies updated.")
        st.rerun()

    # ---- GENERATE QR ----
    if st.button("🔲 Generate Emergency QR", use_container_width=True):
        age = get_age(st.session_state.form_data["dob"])
        payload = {
            "schema_version": "1.0",
            "patient_id": "P-60Y-2026-001",      # static demo ID
            "name": name,
            "age": age,
            "blood_group": blood_group,
            "diabetes": diabetes,
            "allergies": allergies,
            "emergency_contacts": [{"relation": "Son", "name": "Rajesh Sharma", "phone": "+91-9876543210"}],
            "access_url": "http://localhost:8501/Doctor_Dashboard"
        }
        st.session_state.emergency_qr = payload
        st.success("QR generated! Switch to the 'Emergency QR' tab to scan.")

# ============================================================
# TAB 2: EMERGENCY QR
# ============================================================
with tab2:
    st.header("🆘 Emergency QR Card")
    if "emergency_qr" in st.session_state and st.session_state.emergency_qr:
        payload = st.session_state.emergency_qr
        # Generate QR image
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(json.dumps(payload))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(buf, caption="Scan with any camera", width=300)
        with col2:
            st.subheader("Public Emergency Info")
            st.json(payload)
            st.info("Scan to see **name, age, blood group, diabetes status, and allergies**.")
    else:
        st.warning("No QR generated yet. Go to Patient Intake and click 'Generate Emergency QR'.")

# ============================================================
# TAB 3: DOCTOR DASHBOARD
# ============================================================
with tab3:
    st.header("👨‍⚕️ Doctor Dashboard – Full Workup")
    password = st.text_input("Enter Doctor Password", type="password")
    st.caption("🔑 Hint: Password is **1234**")   # visible hint
    if password == "1234":
        st.success("Access granted")
        # Display full premade profile (could also use session data, but keep static for demo clarity)
        p = PREMATURE
        age = get_age(p["dob"])
        st.subheader(f"Patient: {p['name']} (Age: {age})")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Blood Group", p["blood_group"])
            st.metric("Diabetes", p["diabetes"])
            st.write("**Allergies:**", ", ".join(p["allergies"]))
            st.write("**Past Medical History:**", p["past_history"])
            st.write("**Current Medications:**", p["medications"])
        with col2:
            st.write("**Chief Complaint:**", p["chief_complaint"])
            st.write("**Duration:**", p["duration"])
            st.write("**HPI Details:**")
            st.write(f"- Site: {p['site']}")
            st.write(f"- Onset: {p['onset']}")
            st.write(f"- Character: {p['character']}")
            st.write(f"- Associated: {p['associated']}")
            st.write(f"- Severity: {p['severity']}/10")
        st.divider()
        st.subheader("Family & Social History")
        st.write(f"**Family History:** {p['family_history']}")
        st.write(f"**Tobacco:** {p['tobacco']}")
        st.write(f"**Alcohol:** {p['alcohol']}")
        st.write(f"**General ROS:** {p['ros_general']}")
        st.write(f"**Cardio/Resp ROS:** {p['ros_cardio']}")

        # Editable summary simulation
        st.text_area("Edit Summary (simulated)", value=f"{age}yo male with chest pain. Hx of HTN, T2DM. Allergic to Dust & Penicillin. On Metformin and Amlodipine.")
        if st.button("✅ Approve & Push to EMR"):
            st.success("EMR updated successfully (simulated).")
    elif password:
        st.error("Invalid password. Try '1234'.")

# ---------- FOOTER ----------
st.caption("MediKiosk Allopathy Dual‑Tier Demo.")
