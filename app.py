import streamlit as st
import os
import json
import uuid
import pathlib
from typing import Dict, Any, List
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load env variables manually from .env if present
if os.path.exists(".env"):
    try:
        with open(".env") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        os.environ[parts[0].strip()] = parts[1].strip()
    except Exception:
        pass

# Ensure correct imports
from app_workflow import app as workflow_app
from agents.multimodal_processor import MultimodalAgent
from database.drive_db import DriveDatabase

# Google OAuth Setup
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/drive.file",
    "openid"
]

def get_redirect_uri():
    return os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8501/")

# ----------------- Session State Management -----------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "extracted_notes" not in st.session_state:
    st.session_state.extracted_notes = ""

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []

if "google_creds" not in st.session_state:
    st.session_state.google_creds = None

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Sandbox Mode"

# Check redirect params first (OAuth Callback)
query_params = st.query_params
if "code" in query_params:
    code = query_params["code"]
    client_id = os.environ.get("GOOGLE_CLIENT_ID") or st.session_state.get("temp_client_id")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET") or st.session_state.get("temp_client_secret")
    redirect_uri = get_redirect_uri()
    
    if client_id and client_secret:
        try:
            client_config = {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": [redirect_uri]
                }
            }
            flow = Flow.from_client_config(
                client_config=client_config,
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )
            flow.fetch_token(code=code)
            st.session_state.google_creds = flow.credentials
            
            # Fetch user info
            user_info_service = build('oauth2', 'v2', credentials=flow.credentials)
            user_info = user_info_service.userinfo().get().execute()
            st.session_state.user_name = user_info.get("name", "Student")
            st.session_state.user_email = user_info.get("email", "")
            
            st.query_params.clear()
            st.toast("Welcome back! Login successful.", icon="🎉")
        except Exception as e:
            st.error(f"Failed to authenticate: {e}")

# GATING PAGE (if not authenticated)
if not st.session_state.get("google_creds"):
    st.set_page_config(
        page_title="Sign In - FairStudyAI",
        page_icon="🎓",
        layout="centered"
    )
    
    # Custom CSS for the login page
    st.markdown("""
        <style>
        .login-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-top: 50px;
        }
        .login-title {
            background: linear-gradient(135deg, #FF6B6B 0%, #4D96FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .login-subtitle {
            color: #8888aa;
            font-size: 1.1rem;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🎓 FairStudy AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Intelligent Student Workspace</div>', unsafe_allow_html=True)
    
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = get_redirect_uri()
    
    # If not in env, display input fields
    if not client_id or not client_secret:
        st.info("💡 Google OAuth 2.0 Credentials are not configured in your environment. Please supply them below to login.")
        c_id = st.text_input("Google Client ID:", value=st.session_state.get("temp_client_id", ""))
        c_secret = st.text_input("Google Client Secret:", value=st.session_state.get("temp_client_secret", ""), type="password")
        if c_id and c_secret:
            st.session_state.temp_client_id = c_id.strip()
            st.session_state.temp_client_secret = c_secret.strip()
            client_id = c_id.strip()
            client_secret = c_secret.strip()
            
    if client_id and client_secret:
        # Build Authorization Link
        try:
            client_config = {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": [redirect_uri]
                }
            }
            flow = Flow.from_client_config(
                client_config=client_config,
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            st.markdown(f'<a href="{auth_url}" target="_self"><button style="width:100%; padding:12px; background:linear-gradient(135deg, #4D96FF 0%, #6BCB77 100%); color:white; border:none; border-radius:8px; font-weight:600; font-size:1.1rem; cursor:pointer;">Sign in with Google</button></a>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error configuring OAuth: {e}")
    else:
        st.warning("Please configure Client ID and Client Secret to enable Google Sign-In.")
        
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()  # Gate the app

# ----------------- Normal Workspace (Authenticated) -----------------

# Page config with modern title and layout
st.set_page_config(
    page_title="FairStudyAI - Smart Student Workspace",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Premium Custom CSS for custom styling (glassmorphism, gradients, hover effects)
st.markdown("""
    <style>
    /* Gradient Title */
    .title-text {
        background: linear-gradient(135deg, #FF6B6B 0%, #4D96FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .subtitle-text {
        color: #8888aa;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    /* Custom Glassmorphic Card Container */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }

    /* Hover effect for buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #4D96FF 0%, #6BCB77 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(77, 150, 255, 0.3);
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(77, 150, 255, 0.5);
    }

    /* Status Indicator Badge */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 10px;
    }
    .status-connected {
        background-color: rgba(107, 203, 119, 0.2);
        color: #6BCB77;
        border: 1px solid #6BCB77;
    }
    .status-offline {
        background-color: rgba(255, 217, 61, 0.2);
        color: #FFD93D;
        border: 1px solid #FFD93D;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- Helper Functions -----------------

def get_local_sessions() -> List[str]:
    """Retrieves list of saved session IDs from sandbox folder."""
    if not os.path.exists("sandbox_data"):
        return []
    files = os.listdir("sandbox_data")
    return [f.replace(".json", "") for f in files if f.endswith(".json")]

def load_local_session(session_id: str) -> Dict[str, Any]:
    """Loads a session state dict from local sandbox folder."""
    path = f"sandbox_data/{session_id}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

# Load selected session if requested
def change_session(new_id):
    st.session_state.session_id = new_id
    data = load_local_session(new_id)
    if data:
        st.session_state.extracted_notes = data.get("extracted_notes", "")
        st.session_state.quiz_data = data.get("quiz_data", [])
        st.toast(f"Session {new_id} loaded successfully!", icon="📂")

# ----------------- Sidebar (Controls & Authentications) -----------------

with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/education.png", width=100)
    st.markdown("### 🛠️ Workspace Controls")
    
    # User Profile Display
    user_name = st.session_state.get("user_name", "Student")
    user_email = st.session_state.get("user_email", "")
    st.markdown(f"**👤 {user_name}**")
    st.caption(f"📧 {user_email}")
    
    # Session identifier setting
    curr_sess = st.text_input("Active Session ID:", value=st.session_state.session_id)
    if curr_sess != st.session_state.session_id:
        st.session_state.session_id = curr_sess
        
    if st.button("New Study Session"):
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.extracted_notes = ""
        st.session_state.quiz_data = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 📦 Storage & Integration")
    
    # Toggle between local sandbox and google drive
    mode = st.radio("Storage Integration Mode:", ["Sandbox Mode", "Google Drive Mode"])
    st.session_state.auth_mode = mode
    
    if mode == "Sandbox Mode":
        st.markdown(
            '<div class="status-badge status-offline">⚡ Local Sandbox Active (Offline)</div>',
            unsafe_allow_html=True
        )
        st.info("Sessions will be saved inside the local `sandbox_data/` workspace folder.")
    else:
        # Check credentials status
        if st.session_state.google_creds:
            st.markdown(
                '<div class="status-badge status-connected">☁️ Google Drive Connected</div>',
                unsafe_allow_html=True
            )
            if st.button("Sign Out from App"):
                st.session_state.google_creds = None
                st.rerun()

    # Session recovery
    st.markdown("---")
    st.markdown("### 📂 Recover Past Sessions")
    local_sessions = get_local_sessions()
    if local_sessions:
        selected_rec = st.selectbox("Select Session:", local_sessions)
        if st.button("Load Session"):
            change_session(selected_rec)
    else:
        st.caption("No past sessions found in sandbox.")

# ----------------- Main Layout -----------------

st.markdown('<div class="title-text">FairStudy AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">The Multimodal Intelligent Workspace for Students</div>', unsafe_allow_html=True)

# Status notification check for Groq API key
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    st.warning("⚠️ No Groq API Key found in env. Please enter it below to begin.")
    api_key_input = st.text_input("Groq API Key:", type="password")
    if api_key_input:
        os.environ["GROQ_API_KEY"] = api_key_input
        st.success("Groq API key loaded!")
        st.rerun()

# Creating Tabs
tab1, tab2 = st.tabs(["🚀 Study Companion", "✍️ Interactive Quiz"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📥 Upload Materials")
        
        uploaded_file = st.file_uploader(
            "Choose a study file (PDF, Image, or Audio)",
            type=["pdf", "png", "jpg", "jpeg", "mp3", "wav", "m4a"],
            help="Upload your textbook page, lecture audio, or summary notes."
        )
        
        text_prompt = st.text_area(
            "What would you like to focus on?",
            value="Analyze this study material and provide clear, structured notes with key themes.",
            height=100
        )
        
        # Preset Prompt Buttons
        st.markdown("💡 *Quick Presets:*")
        c1, c2, c3 = st.columns(3)
        if c1.button("Summarize Topics"):
            text_prompt = "Create a summary of the core concepts in this study material."
            st.rerun()
        if c2.button("List Equations"):
            text_prompt = "Identify and list all formulas, equations, or scientific laws in the material."
            st.rerun()
        if c3.button("Vocabulary Guide"):
            text_prompt = "Extract key terms, vocabulary words, and definitions."
            st.rerun()

        # Run Workflow
        run_btn = st.button("🔥 Process Study Material")
        
        if run_btn:
            if not uploaded_file:
                st.error("Please upload a file before processing.")
            else:
                # Save uploaded file locally in a temp path inside workspace
                os.makedirs("temp_uploads", exist_ok=True)
                file_path = os.path.join("temp_uploads", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
                with st.spinner("Executing LangGraph Study Workflow..."):
                    try:
                        # Prepare workflow input
                        state_input = {
                            "session_id": st.session_state.session_id,
                            "user_input_path": file_path,
                            "text_prompt": text_prompt,
                            "extracted_notes": "",
                            "quiz_data": [],
                            "next_node": ""
                        }
                        
                        # Run the LangGraph application
                        final_state = workflow_app.invoke(state_input)
                        
                        # Store outputs in session state
                        st.session_state.extracted_notes = final_state.get("extracted_notes", "")
                        st.session_state.quiz_data = final_state.get("quiz_data", [])
                        
                        st.success("Workflow executed and saved state successfully!")
                        st.toast("State saved to storage!", icon="💾")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error executing study workflow: {e}")
                        
    with col2:
        st.markdown("### 📝 Study Notes")
        
        if st.session_state.extracted_notes:
            st.markdown(
                f'<div class="glass-card" style="max-height: 500px; overflow-y: auto;">'
                f'{st.session_state.extracted_notes}'
                f'</div>', 
                unsafe_allow_html=True
            )
            
            # Narration Player (Generates Audio dynamically)
            st.markdown("### 🔊 Audio Narration")
            if st.button("🎙️ Generate Narration"):
                try:
                    with st.spinner("Generating audio narration via Groq/gTTS..."):
                        agent = MultimodalAgent(api_key=os.environ.get("GROQ_API_KEY"))
                        parts = agent.generate_voice_response(st.session_state.extracted_notes[:800]) # Limit length for quick rendering
                        
                        audio_bytes = None
                        for p in parts:
                            if p.inline_data and p.inline_data.data:
                                audio_bytes = p.inline_data.data
                                break
                                
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/wav")
                            st.success("Ready to listen!")
                        else:
                            st.warning("Could not extract raw audio bytes from the response parts.")
                except Exception as e:
                    st.error(f"Failed to generate voice summary: {e}")
        else:
            st.info("Upload study materials and click 'Process Study Material' to view structured notes here.")

with tab2:
    st.markdown("### ✍️ Study Quiz Workspace")
    
    # Button to force quiz generation if they didn't run workflow with "quiz" keyword
    if st.button("🧩 Generate Custom Quiz from Material"):
        if not uploaded_file:
            st.error("Please upload a file in the 'Study Companion' tab first.")
        else:
            os.makedirs("temp_uploads", exist_ok=True)
            file_path = os.path.join("temp_uploads", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            with st.spinner("Designing quiz questions..."):
                try:
                    state_input = {
                        "session_id": st.session_state.session_id,
                        "user_input_path": file_path,
                        "text_prompt": "Create a quiz",
                        "extracted_notes": "",
                        "quiz_data": [],
                        "next_node": ""
                    }
                    final_state = workflow_app.invoke(state_input)
                    st.session_state.quiz_data = final_state.get("quiz_data", [])
                    st.success("Quiz successfully generated! Test your knowledge below.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not generate quiz: {e}")
                    
    # Render Quiz
    if st.session_state.quiz_data:
        st.write("---")
        user_answers = {}
        
        # Display quiz questions
        for idx, q_item in enumerate(st.session_state.quiz_data):
            st.markdown(f"#### Q{idx+1}: {q_item.get('question')}")
            options = q_item.get("options", [])
            
            # Map index letter (A, B, C, D) to option strings
            formatted_options = []
            letter_map = {}
            for i, opt in enumerate(options):
                letter = chr(65 + i) # A, B, C, D
                opt_str = f"{letter}. {opt}"
                formatted_options.append(opt_str)
                letter_map[opt_str] = letter
                
            selection = st.radio(
                f"Choose answer for Question {idx+1}:", 
                formatted_options, 
                key=f"q_{idx}_{st.session_state.session_id}",
                index=None
            )
            if selection:
                user_answers[idx] = letter_map[selection]
                
        # Submit answers and grade
        if st.button("✔️ Submit Quiz Answers"):
            correct_count = 0
            for idx, q_item in enumerate(st.session_state.quiz_data):
                correct_ans = q_item.get("answer", "").strip().upper()
                user_ans = user_answers.get(idx, "")
                
                if user_ans == correct_ans:
                    correct_count += 1
                    st.success(f"Question {idx+1}: Correct! Answer: {correct_ans}")
                else:
                    st.error(f"Question {idx+1}: Incorrect. Your choice: {user_ans if user_ans else 'None'} | Correct Answer: {correct_ans}")
            
            score_percentage = (correct_count / len(st.session_state.quiz_data)) * 100
            st.balloons()
            st.markdown(f"### 🏆 Final Score: **{correct_count} / {len(st.session_state.quiz_data)}** ({score_percentage:.1f}%)")
    else:
        st.info("No active quiz. Generate a quiz above to start your self-assessment!")
