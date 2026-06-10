from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import groq
import os
import time
import pyrebase

# Firebase config
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()

# Groq setup
client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #0a0a0f 100%); }
    .main-title { text-align: center; font-size: 2.5rem; font-weight: 700; background: linear-gradient(90deg, #00d4ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #888; font-size: 1rem; margin-bottom: 30px; }
    .feature-header { background: linear-gradient(90deg, rgba(0,212,255,0.1), rgba(123,47,247,0.1)); border-left: 3px solid #00d4ff; padding: 15px 20px; border-radius: 10px; margin-bottom: 20px; font-size: 1.3rem; font-weight: 600; color: #fff; }
    .response-box { background: rgba(255,255,255,0.05); border: 1px solid rgba(0,212,255,0.2); border-radius: 15px; padding: 20px; margin-top: 15px; color: #ffffff !important; font-size: 1rem; line-height: 1.8; }
    .stButton > button { background: linear-gradient(90deg, #00d4ff, #7b2ff7) !important; color: white !important; border: none !important; border-radius: 25px !important; padding: 10px 30px !important; font-weight: 600 !important; width: 100%; }
    .stTextInput > div > div > input { background: #ffffff !important; border: 1px solid rgba(0,212,255,0.3) !important; border-radius: 10px !important; color: #000000 !important; }
    .stTextArea > div > div > textarea { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(0,212,255,0.3) !important; border-radius: 10px !important; color: white !important; }
    .stSelectbox > div > div { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(0,212,255,0.3) !important; border-radius: 10px !important; }
    .user-badge { background: linear-gradient(90deg, rgba(0,212,255,0.1), rgba(123,47,247,0.1)); border: 1px solid rgba(0,212,255,0.3); border-radius: 20px; padding: 8px 15px; text-align: center; margin-bottom: 15px; color: #00d4ff; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# Session state
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'last_request' not in st.session_state:
    st.session_state['last_request'] = 0
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Response functions
@st.cache_data
def get_cached_response(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def get_response(prompt):
    current_time = time.time()
    if current_time - st.session_state['last_request'] < 3:
        return "⏳ Please wait a moment!"
    st.session_state['last_request'] = current_time
    return get_cached_response(prompt)

# Login page
def login_page():
    st.markdown('<div class="main-title">🎓 Fair Study AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Login to continue</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login 🚀", key="login_btn"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state['user'] = user
                st.session_state['logged_in'] = True
                st.rerun()
            except:
                st.error("Invalid email or password!")

    with tab2:
        email2 = st.text_input("Email", key="signup_email")
        password2 = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Sign Up ✨", key="signup_btn"):
            try:
                user = auth.create_user_with_email_and_password(email2, password2)
                st.session_state['user'] = user
                st.session_state['logged_in'] = True
                st.rerun()
            except Exception as e:
                st.error(f"Signup failed! {str(e)}")

# Main app
if not st.session_state['logged_in']:
    login_page()
else:
    # Sidebar
    st.sidebar.markdown('<div class="user-badge">👤 Logged In</div>', unsafe_allow_html=True)
    if st.sidebar.button("Logout 🚪"):
        st.session_state['user'] = None
        st.session_state['logged_in'] = False
        st.rerun()

    feature = st.sidebar.selectbox("Choose a Feature", [
        "💡 Concept Explainer",
        "📝 Smart Note Generator",
        "🤖 Doubt Solver",
        "🎯 Quiz Generator",
        "📄 Text Summarizer",
        "💬 General Chat",
    ])

    language = st.sidebar.selectbox("Response Language", [
        "English", "Tamil", "Hindi",
    ])

    st.sidebar.markdown("---")
    st.sidebar.markdown("**🌍 UN SDG Goal 4 — Quality Education**")
    st.sidebar.markdown("Built for Google Solution Challenge 2026")

    # Header
    st.markdown('<div class="main-title">🎓 Fair Study AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Your unbiased AI-powered learning assistant</div>', unsafe_allow_html=True)

    # Features
    if feature == "💡 Concept Explainer":
        st.markdown('<div class="feature-header">💡 Concept Explainer</div>', unsafe_allow_html=True)
        topic = st.text_input("Enter a topic:")
        level = st.selectbox("Your level:", ["Beginner", "Intermediate", "Advanced"])
        if st.button("Explain! 🚀"):
            if topic:
                with st.spinner("🤔 Thinking..."):
                    prompt = f"Explain '{topic}' for a {level} college student clearly. Respond in {language}."
                    result = get_response(prompt)
                    st.markdown(f'<div class="response-box">{result}</div>', unsafe_allow_html=True)

    elif feature == "📝 Smart Note Generator":
        st.markdown('<div class="feature-header">📝 Smart Note Generator</div>', unsafe_allow_html=True)
        subject = st.text_input("Enter subject:")
        if st.button("Generate Notes! 📚"):
            if subject:
                with st.spinner("📝 Generating..."):
                    prompt = f"Generate structured study notes for '{subject}' for college students. Respond in {language}."
                    result = get_response(prompt)
                    st.markdown(f'<div class="response-box">{result}</div>', unsafe_allow_html=True)

    elif feature == "🤖 Doubt Solver":
        st.markdown('<div class="feature-header">🤖 Doubt Solver</div>', unsafe_allow_html=True)
        doubt = st.text_area("Type your doubt:")
        if st.button("Solve! ⚡"):
            if doubt:
                with st.spinner("🔍 Solving..."):
                    prompt = f"Answer this college student doubt clearly: {doubt}. Respond in {language}."
                    result = get_response(prompt)
                    st.markdown(f'<div class="response-box">{result}</div>', unsafe_allow_html=True)

    elif feature == "🎯 Quiz Generator":
        st.markdown('<div class="feature-header">🎯 Quiz Generator</div>', unsafe_allow_html=True)
        topic = st.text_input("Enter topic for quiz:")
        num = st.slider("Number of questions:", 3, 10, 5)
        if st.button("Generate Quiz! 🎯"):
            if topic:
                with st.spinner("🎯 Generating quiz..."):
                    prompt = f"Generate {num} MCQ questions with 4 options and answers for '{topic}'. Respond in {language}."
                    result = get_response(prompt)
                    st.markdown(f'<div class="response-box">{result}</div>', unsafe_allow_html=True)

    elif feature == "📄 Text Summarizer":
        st.markdown('<div class="feature-header">📄 Text Summarizer</div>', unsafe_allow_html=True)
        text = st.text_area("Paste your text here:", height=200)
        if st.button("Summarize! 📄"):
            if text:
                with st.spinner("📄 Summarizing..."):
                    prompt = f"Summarize this text for a college student: {text}. Respond in {language}."
                    result = get_response(prompt)
                    st.markdown(f'<div class="response-box">{result}</div>', unsafe_allow_html=True)

    elif feature == "💬 General Chat":
        st.markdown('<div class="feature-header">💬 General Chat</div>', unsafe_allow_html=True)
        for chat in st.session_state['chat_history']:
            if chat["role"] == "user":
                st.markdown(f"**You:** {chat['content']}")
            else:
                st.markdown(f'<div class="response-box">🤖 {chat["content"]}</div>', unsafe_allow_html=True)
        user_input = st.text_input("Type your message:", key="chat_input")
        col1, col2 = st.columns([3,1])
        with col1:
            if st.button("Send! 💬"):
                if user_input:
                    st.session_state['chat_history'].append({"role": "user", "content": user_input})
                    with st.spinner("Thinking..."):
                        prompt = f"You are a helpful AI assistant. User says: {user_input}. Respond in {language}."
                        result = get_response(prompt)
                        st.session_state['chat_history'].append({"role": "assistant", "content": result})
                    st.rerun()
        with col2:
            if st.button("Clear 🗑️"):
                st.session_state['chat_history'] = []
                st.rerun()