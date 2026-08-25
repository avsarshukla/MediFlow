import streamlit as st
import qrcode
from io import BytesIO
import json
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

# ---------- SESSION STATE INITIALIZATION ----------
if "form_data" not in st.session_state:
    st.session_state.form_data = {k: v for k, v in PREMATURE.items()}

if "audio_transcript" not in st.session_state:
    st.session_state.audio_transcript = ""

if "ocr_extracted_text" not in st.session_state:
    st.session_state.ocr_extracted_text = ""

if "last_processed_audio_id" not in st.session_state:
    st.session_state.last_processed_audio_id = None

if "last_processed_file_name" not in st.session_state:
    st.session_state.last_processed_file_name = None

# Cache OCR reader model to load into memory only once
@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['en'], gpu=False)

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="MediKiosk Demo", layout="wide")
st.title("🏥 MediKiosk – Allopathy Dual-Tier Demo")

# ---------- HELPER: compute age from DOB ----------
def get_age(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except Exception:
        return None

# ---------- TABS ----------
tab1, tab2, tab3 = st.tabs(["📋 Patient Intake (15 Questions)", "🆘 Emergency QR", "👨‍⚕️ Doctor Dashboard"])

# ============================================================
# TAB 1: PATIENT INTAKE
# ============================================================
with tab1:
    st.header("Patient Intake – 15 Crucial Questions")
    st.caption("Pre-filled with the demo profile. Edit manually or populate via Voice/Document OCR below.")

    # --- Live Voice Intake (ASR) ---
    st.subheader("🎙️ Live Voice Intake (ASR)")
    audio_val = st.audio_input("Record Patient Voice Intake")
    
    if audio_val is not None:
        audio_id = audio_val.file_id if hasattr(audio_val, "file_id") else audio_val.name
        if st.session_state.last_processed_audio_id != audio_id:
            with st.spinner("Transcribing audio input..."):
                try:
                    r = sr.Recognizer()
                    with sr.AudioFile(audio_val) as source:
                        audio_data = r.record(source)
                        transcription = r.recognize_google(audio_data)
                    
                    st.session_state.audio_transcript = transcription
                    st.session_state.last_processed_audio_id = audio_id
                    
                    # Update fields based on transcription content
                    text_lower = transcription.lower()
                    if "chest pain" in text_lower:
                        st.session_state.form_data["reason"] = transcription
                    if "diabetes" in text_lower or "type 2" in text_lower:
                        st.session_state.form_data["diabetes"] = "Type 2"
                    if "dust" in text_lower and "Environmental/Dust" not in st.session_state.form_data["allergies"]:
                        st.session_state.form_data["allergies"].append("Environmental/Dust")
                    
                    st.success(f"Transcribed: \"{transcription}\"")
                    st.rerun()
                except sr.UnknownValueError:
                    st.warning("Speech recognition could not understand audio. Please re-record.")
                    st.session_state.last_processed_audio_id = audio_id
                except Exception as e:
                    st.error(f"Audio processing error: {e}")
                    st.session_state.last_processed_audio_id = audio_id

    # --- Upload Document (PDF / OCR) ---
    st.subheader("📄 Upload Document (PDF Parsing & OCR)")
    uploaded_file = st.file_uploader("Upload Medical Record or Prescription (PDF/Image)", type=["png", "jpg", "jpeg", "pdf"])
    
    if uploaded_file is not None:
        file_identifier = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.last_processed_file_name != file_identifier:
            extracted_text = ""
            with st.spinner("Processing document..."):
                try:
                    if uploaded_file.type == "application/pdf" or uploaded_file.name.lower().endswith(".pdf"):
                        pdf_stream = BytesIO(uploaded_file.getvalue())
                        reader = pypdf.PdfReader(pdf_stream)
                        for page_idx, page in enumerate(reader.pages):
                            page_text = page.extract_text()
                            if page_text:
                                extracted_text += page_text + "\n"
                        
                        # Fallback for scanned PDF pages containing zero selectable text
                        if not extracted_text.strip():
                            extracted_text = "PDF scanned without embedded text. Upload as PNG/JPG for OCR."
                    else:
                        ocr_reader = load_ocr_reader()
                        img = Image.open(uploaded_file).convert("RGB")
                        img_np = np.array(img)
                        ocr_results = ocr_reader.readtext(img_np, detail=0)
                        extracted_text = "\n".join(ocr_results)
                    
                    st.session_state.ocr_extracted_text = extracted_text
                    st.session_state.last_processed_file_name = file_identifier
                    
                    # Basic keyword autofill from OCR text
                    text_lower = extracted_text.lower()
                    if "type 2" in text_lower or "diabetes" in text_lower:
                        st.session_state.form_data["diabetes"] = "Type 2"
                    if "metformin" in text_lower:
                        st.session_state.form_data["medications"] = extracted_text.strip()
                    
                    st.success("Document parsed successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error parsing document: {e}")
                    st.session_state.last_processed_file_name = file_identifier

    st.divider()

    # --- Form Inputs ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Demographics")
        name = st.text_input("**1. Full Name**", value=st.session_state.form_data["name"])
        dob = st.date_input("**2. Date of Birth**", value=datetime.strptime(st.session_state.form_data["dob"], "%Y-%m-%d"))
        
        blood_options = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
        current_bg = st.session_state.form_data["blood_group"]
        bg_idx = blood_options.index(current_bg) if current_bg in blood_options else 0
        blood_group = st.selectbox("**3. Blood Group**", blood_options, index=bg_idx)

        st.subheader("Chief Complaint & HPI")
        reason = st.text_area("**4. Main Reason for Visit Today**", value=st.session_state.form_data["reason"], height=70)
        duration = st.text_input("**5. Symptom Duration**", value=st.session_state.form_data["duration"])
        location_radiation = st.text_input("**6. Symptom Location & Radiation**", value=st.session_data if "session_data" in locals() else st.session_state.form_data["location_radiation"])
        onset = st.text_input("**7. Onset Type**", value=st.session_state.form_data["onset"])
        character = st.text_input("**8. Symptom Character**", value=st.session_state.form_data["character"])
        severity = st.slider("**9. Pain/Severity Scale (0–10)**", 0, 10, value=int(st.session_state.form_data["severity"]))

    with col2:
        st.subheader("Past Medical & Surgical")
        diabetes_options = ["No", "Type 1", "Type 2", "Gestational", "Pre-diabetes"]
        current_diabetes = st.session_state.form_data["diabetes"]
        diabetes_idx = diabetes_options.index(current_diabetes) if current_diabetes in diabetes_options else 0
        diabetes = st.selectbox("**10. Diabetes Diagnosis**", diabetes_options, index=diabetes_idx)
        
        past_surgeries = st.text_area("**11. Major Past Diagnoses & Prior Surgeries**", value=st.session_state.form_data["past_surgeries"], height=70)

        st.subheader("Drug & Allergy History")
        medications = st.text_area("**12. Current Prescription Medications & Dosages**", value=st.session_state.form_data["medications"], height=70)
        
        allergy_options = ["Environmental/Dust", "Nuts/Food", "Medication", "Latex", "Other"]
        active_allergies = [a for a in st.session_state.form_data["allergies"] if a in allergy_options]
        allergies = st.multiselect("**13. Specific Allergies & Reactions**", allergy_options, default=active_allergies)

        st.subheader("Personal & Social History")
        tobacco_alcohol = st.text_area("**14. Tobacco, Vaping, & Alcohol Use**", value=st.session_state.form_data["tobacco_alcohol"], height=70)

        st.subheader("Review of Systems")
        cardio_resp = st.text_area("**15. Cardiovascular & Respiratory Symptoms**", value=st.session_state.form_data["cardio_resp"], height=70)

    # Sync manual input updates to session state
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

    st.divider()
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
        st.success("QR generated! Navigate to the 'Emergency QR' tab to view.")

# ============================================================
# TAB 2: EMERGENCY QR
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

# ============================================================
# TAB 3: DOCTOR DASHBOARD
# ============================================================
with tab3:
    st.header("👨‍⚕️ Doctor Dashboard – Full Workup")
    password = st.text_input("Enter Doctor Password (Press Enter)", type="password", key="doc_pwd")
    
    if password == "1234":
        st.success("Access Granted")
        f = st.session_state.form_data
        age = get_age(f["dob"])
        st.subheader(f"Patient: {f['name']} (Age: {age})")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Blood Group", f["blood_group"])
            st.metric("Diabetes", f["diabetes"])
            st.write("**Allergies:**", ", ".join(f["allergies"]) if f["allergies"] else "None reported")
            st.write("**Past Diagnoses & Surgeries:**", f["past_surgeries"])
            st.write("**Current Medications:**", f["medications"])
            st.write("**Tobacco/Alcohol:**", f["tobacco_alcohol"])
        with col2:
            st.write("**Main Reason:**", f["reason"])
            st.write("**Duration:**", f["duration"])
            st.write("**Location & Radiation:**", f["location_radiation"])
            st.write("**Onset:**", f["onset"])
            st.write("**Character:**", f["character"])
            st.write(f"**Severity:** {f['severity']}/10")
            st.write("**Cardio/Resp:**", f["cardio_resp"])
            
        st.divider()
        st.subheader("📥 Raw Intake Feeds (Voice & OCR)")
        
        col_audio, col_ocr = st.columns(2)
        with col_audio:
            st.markdown("##### 🎙️ Audio Transcription (ASR)")
            if st.session_state.audio_transcript:
                st.info(st.session_state.audio_transcript)
            else:
                st.caption("No audio recording captured for this session.")

        with col_ocr:
            st.markdown("##### 📄 Parsed Document Text (OCR / PDF)")
            if st.session_state.ocr_extracted_text:
                st.text_area("Extracted Document Content", value=st.session_state.ocr_extracted_text, height=130, disabled=True)
            else:
                st.caption("No prescription or document uploaded for this session.")

        st.divider()
        summary = (
            f"{age}yo patient presenting with {f['reason'].lower()}. "
            f"Hx: {f['past_surgeries']}. Allergies: {', '.join(f['allergies']) if f['allergies'] else 'NKDA'}. "
            f"Meds: {f['medications']}."
        )
        st.text_area("Edit Clinical Summary", value=summary, height=100)
        
        if st.button("✅ Approve & Push to EMR", use_container_width=True):
            st.success("EMR updated successfully.")
            
    elif password:
        st.error("Invalid password. Enter '1234'.")
