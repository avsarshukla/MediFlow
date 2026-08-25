import streamlit as st
import qrcode
from io import BytesIO
import json
import time
from datetime import datetime

# ---------- PREMADE 60‑YEAR‑OLD PROFILE ----------
PREMATURE = {
    "name": "Ramesh Sharma",
    "dob": "1966-03-15",                        # ~60 years
    "blood_group": "O+",
    "reason": "Acute substernal chest pain radiating to left arm",
    "duration": "45 minutes",
    "location_radiation": "Substernal, radiating to left arm and jaw",
    "onset": "Acute while walking",
    "character": "Squeezing / Heavy",
    "severity": 8,
    "diabetes": "Type 2",
    "past_surgeries": "Hypertension (10 yrs), Type 2 Diabetes (8 yrs), No surgeries",
    "medications": "Metformin 500mg BD, Amlodipine 5mg OD",
    "allergies": ["Environmental/Dust", "Medication"],   # dust and penicillin
    "tobacco_alcohol": "Never smoker, occasional alcohol",
    "cardio_resp": "Chest tightness, no SOB at rest"
}

# ---------- SESSION STATE ----------
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "name": PREMATURE["name"],
        "dob": PREMATURE["dob"],
        "blood_group": PREMATURE["blood_group"],
        "reason": PREMATURE["reason"],
        "duration": PREMATURE["duration"],
        "location_radiation": PREMATURE["location_radiation"],
        "onset": PREMATURE["onset"],
        "character": PREMATURE["character"],
        "severity": PREMATURE["severity"],
        "diabetes": PREMATURE["diabetes"],
        "past_surgeries": PREMATURE["past_surgeries"],
        "medications": PREMATURE["medications"],
        "allergies": PREMATURE["allergies"],
        "tobacco_alcohol": PREMATURE["tobacco_alcohol"],
        "cardio_resp": PREMATURE["cardio_resp"],
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
tab1, tab2, tab3 = st.tabs(["📋 Patient Intake (15 Questions)", "🆘 Emergency QR", "👨‍⚕️ Doctor Dashboard"])

# ============================================================
# TAB 1: PATIENT INTAKE
# ============================================================
with tab1:
    st.header("Patient Intake – 15 Crucial Questions")
    st.caption("Pre‑filled with the demo 60‑year‑old profile. Edit as needed.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Demographics")
        # 1. Full Name
        name = st.text_input("**1. Full Name**", value=st.session_state.form_data["name"])
        # 2. Date of Birth
        dob = st.date_input("**2. Date of Birth**", value=datetime.strptime(st.session_state.form_data["dob"], "%Y-%m-%d"))
        # 3. Blood Group
        blood_group = st.selectbox(
            "**3. Blood Group**",
            ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"],
            index=["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"].index(st.session_state.form_data["blood_group"])
        )

        st.subheader("Chief Complaint & HPI")
        # 4. Main Reason for Visit
        reason = st.text_area("**4. Main Reason for Visit Today**", value=st.session_state.form_data["reason"], height=70)
        # 5. Symptom Duration
        duration = st.text_input("**5. Symptom Duration**", value=st.session_state.form_data["duration"])
        # 6. Symptom Location & Radiation
        location_radiation = st.text_input("**6. Symptom Location & Radiation**", value=st.session_state.form_data["location_radiation"])
        # 7. Onset Type
        onset = st.text_input("**7. Onset Type**", value=st.session_state.form_data["onset"])
        # 8. Symptom Character
        character = st.text_input("**8. Symptom Character**", value=st.session_state.form_data["character"])
        # 9. Pain/Severity Scale (0-10)
        severity = st.slider("**9. Pain/Severity Scale (0–10)**", 0, 10, value=st.session_state.form_data["severity"])

    with col2:
        st.subheader("Past Medical & Surgical")
        # 10. Diabetes Diagnosis
        diabetes = st.selectbox(
            "**10. Diabetes Diagnosis**",
            ["No", "Type 1", "Type 2", "Gestational", "Pre‑diabetes"],
            index=["No","Type 1","Type 2","Gestational","Pre‑diabetes"].index(st.session_state.form_data["diabetes"])
        )
        # 11. Major Past Diagnoses & Prior Surgeries
        past_surgeries = st.text_area("**11. Major Past Diagnoses & Prior Surgeries**", value=st.session_state.form_data["past_surgeries"], height=70)

        st.subheader("Drug & Allergy History")
        # 12. Current Prescription Medications & Dosages
        medications = st.text_area("**12. Current Prescription Medications & Dosages**", value=st.session_state.form_data["medications"], height=70)
        # 13. Specific Allergies & Reactions
        allergy_options = ["Environmental/Dust", "Nuts/Food", "Medication", "Latex", "Other"]
        allergies = st.multiselect(
            "**13. Specific Allergies & Reactions**",
            allergy_options,
            default=[a for a in st.session_state.form_data["allergies"] if a in allergy_options]
        )
        other_allergy = ""
        if "Other" in allergies:
            other_allergy = st.text_input("Please specify other allergies")
        if other_allergy:
            allergies = [a for a in allergies if a != "Other"] + [other_allergy]
        else:
            allergies = [a for a in allergies if a != "Other"]

        st.subheader("Personal & Social History")
        # 14. Tobacco, Vaping, & Alcohol Use
        tobacco_alcohol = st.text_area("**14. Tobacco, Vaping, & Alcohol Use**", value=st.session_state.form_data["tobacco_alcohol"], height=70)

        st.subheader("Review of Systems")
        # 15. Cardiovascular & Respiratory Symptoms
        cardio_resp = st.text_area("**15. Cardiovascular & Respiratory Symptoms**", value=st.session_state.form_data["cardio_resp"], height=70)

    # Update session state with all inputs
    st.session_state.form_data.update({
        "name": name,
        "dob": dob.strftime("%Y-%m-%d"),
        "blood_group": blood_group,
        "reason": reason,
        "duration": duration,
        "location_radiation": location_radiation,
        "onset": onset,
        "character": character,
        "severity": severity,
        "diabetes": diabetes,
        "past_surgeries": past_surgeries,
        "medications": medications,
        "allergies": allergies,
        "tobacco_alcohol": tobacco_alcohol,
        "cardio_resp": cardio_resp,
    })

    # ---- SIMULATED VOICE ----
    if st.button("🎤 Simulate Voice Intake", use_container_width=True):
        with st.spinner("Processing voice input..."):
            time.sleep(1.5)
            st.session_state.form_data.update({
                "reason": PREMATURE["reason"],
                "duration": PREMATURE["duration"],
                "location_radiation": PREMATURE["location_radiation"],
                "onset": PREMATURE["onset"],
                "character": PREMATURE["character"],
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
            st.write("Identifying diabetes, allergies, and medications...")
            time.sleep(0.8)
            st.session_state.form_data.update({
                "diabetes": PREMATURE["diabetes"],
                "allergies": PREMATURE["allergies"],
                "medications": PREMATURE["medications"],
            })
            status.update(label="OCR complete!", state="complete")
        st.success("Prescription parsed! Diabetes, allergies & medications updated.")
        st.rerun()

    # ---- GENERATE QR ----
    if st.button("🔲 Generate Emergency QR", use_container_width=True):
        age = get_age(st.session_state.form_data["dob"])
        # Simple payload – only essential info
        payload = {
            "patient_id": "P-60Y-2026-001",      # static demo ID
            "name": name,
            "age": age,
            "blood_group": blood_group,
            "diabetes": diabetes,
            "allergies": allergies,
            "emergency_contact": "+91-9876543210 (Son: Rajesh)"
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
            st.info("Scan reveals: **name, age, blood group, diabetes, allergies, and emergency contact**.")
    else:
        st.warning("No QR generated yet. Go to Patient Intake and click 'Generate Emergency QR'.")

# ============================================================
# TAB 3: DOCTOR DASHBOARD
# ============================================================
with tab3:
    st.header("👨‍⚕️ Doctor Dashboard – Full Workup")
    password = st.text_input("Enter Doctor Password", type="password")
    st.caption("🔑 Hint: Password is **1234**")
    if password == "1234":
        st.success("Access granted")
        # Use current form data (or fallback to PREMATURE)
        f = st.session_state.form_data
        age = get_age(f["dob"])
        st.subheader(f"Patient: {f['name']} (Age: {age})")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Blood Group", f["blood_group"])
            st.metric("Diabetes", f["diabetes"])
            st.write("**Allergies:**", ", ".join(f["allergies"]))
            st.write("**Past Diagnoses & Surgeries:**", f["past_surgeries"])
            st.write("**Current Medications:**", f["medications"])
            st.write("**Tobacco/Alcohol:**", f["tobacco_alcohol"])
        with col2:
            st.write("**Main Reason for Visit:**", f["reason"])
            st.write("**Duration:**", f["duration"])
            st.write("**Location & Radiation:**", f["location_radiation"])
            st.write("**Onset Type:**", f["onset"])
            st.write("**Symptom Character:**", f["character"])
            st.write(f"**Severity:** {f['severity']}/10")
            st.write("**Cardio/Resp Symptoms:**", f["cardio_resp"])
        st.divider()
        # Editable summary simulation
        summary = f"{age}yo patient with {f['reason'].lower()}. Hx: {f['past_surgeries']}. Allergies: {', '.join(f['allergies'])}. Meds: {f['medications']}."
        st.text_area("Edit Summary (simulated)", value=summary)
        if st.button("✅ Approve & Push to EMR"):
            st.success("EMR updated successfully (simulated).")
    elif password:
        st.error("Invalid password. Try '1234'.")

# ---------- FOOTER ----------
st.caption("MediKiosk Allopathy Dual‑Tier Demo.")
