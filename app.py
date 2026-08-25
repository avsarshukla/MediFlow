import streamlit as st
import qrcode
from io import BytesIO
import json
import time
from datetime import datetime
import speech_recognition as sr
import pypdf
import easyocr
import numpy as np
from PIL import Image

# ---------- PREMADE 60-YEAR-OLD PROFILE ----------
PREMATURE = {
    "name": "Ramesh Sharma",
    "dob": "1966-03-15",
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
    "allergies": ["Environmental/Dust", "Medication"],
    "tobacco_alcohol": "Never smoker, occasional alcohol",
    "cardio_resp": "Chest tightness, no SOB at rest"
}

# ---------- SESSION STATE ----------
if "form_data" not in st.session_state:
    st.session_state.form_data = {k: v for k, v in PREMATURE.items()}

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="MediKiosk Demo", layout="wide")
st.title("🏥 MediKiosk – Allopathy Dual-Tier Demo")

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
    st.caption("Pre-filled with the demo 60-year-old profile. Edit as needed.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Demographics")
        name = st.text_input("**1. Full Name**", value=st.session_state.form_data["name"])
        dob = st.date_input("**2. Date of Birth**", value=datetime.strptime(st.session_state.form_data["dob"], "%Y-%m-%d"))
        blood_group = st.selectbox(
            "**3. Blood Group**",
            ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"],
            index=["A+","A-","B+","B-","AB+","AB-","O+","O-","Unknown"].index(st.session_state.form_data["blood_group"])
        )

        st.subheader("Chief Complaint & HPI")
        reason = st.text_area("**4. Main Reason for Visit Today**", value=st.session_state.form_data["reason"], height=70)
        duration = st.text_input("**5. Symptom Duration**", value=st.session_state.form_data["duration"])
        location_radiation = st.text_input("**6. Symptom Location & Radiation**", value=st.session_state.form_data["location_radiation"])
        onset = st.text_input("**7. Onset Type**", value=st.session_state.form_data["onset"])
        character = st.text_input("**8. Symptom Character**", value=st.session_state.form_data["character"])
        severity = st.slider("**9. Pain/Severity Scale (0–10)**", 0, 10, value=st.session_state.form_data["severity"])

    with col2:
        st.subheader("Past Medical & Surgical")
        diabetes = st.selectbox(
            "**10. Diabetes Diagnosis**",
            ["No", "Type 1", "Type 2", "Gestational", "Pre-diabetes"],
            index=["No","Type 1","Type 2","Gestational","Pre-diabetes"].index(st.session_state.form_data["diabetes"])
        )
        past_surgeries = st.text_area("**11. Major Past Diagnoses & Prior Surgeries**", value=st.session_state.form_data["past_surgeries"], height=70)

        st.subheader("Drug & Allergy History")
        medications = st.text_area("**12. Current Prescription Medications & Dosages**", value=st.session_state.form_data["medications"], height=70)
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
        tobacco_alcohol = st.text_area("**14. Tobacco, Vaping, & Alcohol Use**", value=st.session_state.form_data["tobacco_alcohol"], height=70)

        st.subheader("Review of Systems")
        cardio_resp = st.text_area("**15. Cardiovascular & Respiratory Symptoms**", value=st.session_state.form_data["cardio_resp"], height=70)

    # Update session state with all manual inputs
    st.session_state.form_data.update({
        "name": name, "dob": dob.strftime("%Y-%m-%d"), "blood_group": blood_group,
        "reason": reason, "duration": duration, "location_radiation": location_radiation,
        "onset": onset, "character": character, "severity": severity, "diabetes": diabetes,
        "past_surgeries": past_surgeries, "medications": medications, "allergies": allergies,
        "tobacco_alcohol": tobacco_alcohol, "cardio_resp": cardio_resp,
    })

    st.divider()
    st.subheader("🎙️ Live Voice Intake (ASR)")
    st.info("Speak your symptoms (e.g., 'I have severe chest pain and a history of Type 2 diabetes').")
    
    # st.audio_input is available in Streamlit 1.36+
    audio_val = st.audio_input("Record Voice Intake")
    if audio_val:
        with st.spinner("Transcribing..."):
            try:
                r = sr.Recognizer()
                with sr.AudioFile(audio_val) as source:
                    audio_data = r.record(source)
                    transcription = r.recognize_google(audio_data)
                
                st.success(f"**Transcribed Speech:** {transcription}")
                
                # Basic keyword mapping for demonstration
                text_lower = transcription.lower()
                if "chest pain" in text_lower: st.session_state.form_data["reason"] = "Chest pain (Extracted via Voice)"
                if "diabetes" in text_lower or "type 2" in text_lower: st.session_state.form_data["diabetes"] = "Type 2"
                if "dust" in text_lower: st.session_state.form_data["allergies"].append("Environmental/Dust")
                
                st.info("Fields updated based on speech recognition. Refresh or check above to see changes.")
            except sr.UnknownValueError:
                st.error("Google Speech Recognition could not understand the audio.")
            except Exception as e:
                st.error(f"Error processing audio: {e}")

    st.divider()
    st.subheader("📄 Upload Document (PDF Parsing & OCR)")
    uploaded_file = st.file_uploader("Upload Medical Record or Prescription (PDF/Image)", type=["png", "jpg", "jpeg", "pdf"])
    
    if uploaded_file is not None:
        extracted_text = ""
        with st.status("Parsing document...", expanded=True) as status:
            if uploaded_file.type == "application/pdf":
                st.write("Parsing direct PDF using `pypdf`...")
                reader = pypdf.PdfReader(uploaded_file)
                for page in reader.pages:
                    extracted_text += page.extract_text() + "\n"
            else:
                st.write("Parsing image using `EasyOCR` (No system dependencies required)...")
                reader = easyocr.Reader(['en'])
                image = Image.open(uploaded_file)
                image_np = np.array(image)
                results = reader.readtext(image_np, detail=0)
                extracted_text = " ".join(results)
                
            status.update(label="Parsing complete!", state="complete")
        
        st.write("**Extracted Text:**")
        st.text(extracted_text)

        # Basic keyword mapping for demonstration
        text_lower = extracted_text.lower()
        if "type 2" in text_lower: st.session_state.form_data["diabetes"] = "Type 2"
        if "metformin" in text_lower: st.session_state.form_data["medications"] = "Metformin detected"
        
        st.success("Document parsed! Corresponding fields updated.")

    st.divider()
    # ---- GENERATE QR ----
    if st.button("🔲 Generate Emergency QR", use_container_width=True):
        age = get_age(st.session_state.form_data["dob"])
        payload = {
            "patient_id": "P-60Y-2026-001",
            "name": st.session_state.form_data["name"],
            "age": age,
            "blood_group": st.session_state.form_data["blood_group"],
            "diabetes": st.session_state.form_data["diabetes"],
            "allergies": st.session_state.form_data["allergies"],
            "emergency_contact": "+91-9876543210 (Son: Rajesh)"
        }
        st.session_state.emergency_qr = payload
        st.success("QR generated! Switch to the 'Emergency QR' tab to scan.")

# ============================================================
# TAB 2 & 3: EMERGENCY QR & DOCTOR DASHBOARD (Unchanged Logic)
# ============================================================
with tab2:
    st.header("🆘 Emergency QR Card")
    if "emergency_qr" in st.session_state and st.session_state.emergency_qr:
        payload = st.session_state.emergency_qr
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
    else:
        st.warning("No QR generated yet. Go to Patient Intake and click 'Generate Emergency QR'.")

with tab3:
    st.header("👨‍⚕️ Doctor Dashboard – Full Workup")
    password = st.text_input("Enter Doctor Password", type="password")
    if password == "1234":
        st.success("Access granted")
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
            st.write("**Main Reason:**", f["reason"])
            st.write("**Duration:**", f["duration"])
            st.write("**Location:**", f["location_radiation"])
            st.write("**Onset:**", f["onset"])
            st.write("**Character:**", f["character"])
            st.write(f"**Severity:** {f['severity']}/10")
            st.write("**Cardio/Resp:**", f["cardio_resp"])
        st.divider()
        summary = f"{age}yo patient with {f['reason'].lower()}. Hx: {f['past_surgeries']}. Allergies: {', '.join(f['allergies'])}. Meds: {f['medications']}."
        st.text_area("Edit Summary", value=summary)₹
