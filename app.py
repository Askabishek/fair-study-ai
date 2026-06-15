import streamlit as st
import os
import time
import groq

client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Rate limiting + Caching
if 'last_request' not in st.session_state:
    st.session_state.last_request = 0

@st.cache_data
def get_cached_response(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def get_response(prompt):
    current_time = time.time()
    if current_time - st.session_state.last_request < 3:
        return "⏳ Please wait a moment before the next request!"
    st.session_state.last_request = current_time
    return get_cached_response(prompt)

# Page config
st.set_page_config(page_title="Fair Study AI", page_icon="🎓", layout="wide")

# Glassmorphism Dark UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* Reset & Base */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080b14 !important;
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}

[data-testid="stAppViewContainer"] {
    background: 
        radial-gradient(ellipse at 20% 10%, rgba(99, 102, 241, 0.12) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.10) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(6, 182, 212, 0.05) 0%, transparent 70%),
        #080b14 !important;
    min-height: 100vh;
}

[data-testid="stHeader"] { background: transparent !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15, 20, 40, 0.85) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
}

[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Sidebar logo area */
.sidebar-logo {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
    border-bottom: 1px solid rgba(99, 102, 241, 0.2);
    margin-bottom: 1.5rem;
}

.sidebar-logo h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #818cf8, #c084fc, #22d3ee) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: -0.02em;
}

.sidebar-logo p {
    font-size: 0.75rem !important;
    color: rgba(148, 163, 184, 0.8) !important;
    margin-top: 0.3rem;
    -webkit-text-fill-color: rgba(148, 163, 184, 0.8) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: rgba(30, 35, 60, 0.6) !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    transition: border-color 0.2s ease;
}

[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(99, 102, 241, 0.5) !important;
}

/* Main content area */
.main .block-container {
    padding: 2rem 2.5rem !important;
    max-width: 900px !important;
}

/* Page header */
.page-header {
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid rgba(99, 102, 241, 0.15);
}

.page-header h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818cf8 0%, #c084fc 60%, #22d3ee 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
    line-height: 1.2;
}

.page-header p {
    font-size: 0.88rem;
    color: rgba(148, 163, 184, 0.75);
    margin-top: 0.4rem;
}

/* Glass card */
.glass-card {
    background: rgba(20, 25, 50, 0.55);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(99, 102, 241, 0.18);
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.04);
}

/* Result card */
.result-card {
    background: rgba(15, 20, 45, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-left: 3px solid #818cf8;
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    margin-top: 1.2rem;
    line-height: 1.75;
    font-size: 0.95rem;
    color: #cbd5e1;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

/* Text inputs */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(20, 25, 55, 0.6) !important;
    border: 1px solid rgba(99, 102, 241, 0.22) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    padding: 0.7rem 1rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(99, 102, 241, 0.55) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    outline: none !important;
}

[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
    color: rgba(148, 163, 184, 0.9) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em;
}

/* Button */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.8rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35) !important;
}

[data-testid="stButton"] button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    background: linear-gradient(135deg, #7c3aed, #9333ea) !important;
}

[data-testid="stButton"] button:active {
    transform: translateY(0px) !important;
}

/* Slider */
[data-testid="stSlider"] {
    padding: 0.5rem 0 !important;
}

/* Spinner */
[data-testid="stSpinner"] {
    color: #818cf8 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(15, 20, 40, 0.5); }
::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.6); }

/* Feature badge */
.feature-badge {
    display: inline-block;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 500;
    color: #a5b4fc;
    margin-bottom: 1rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Hide streamlit default elements */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h1>🎓 Fair Study AI</h1>
        <p>Unbiased AI learning assistant</p>
    </div>
    """, unsafe_allow_html=True)

    feature = st.selectbox("✦ Feature", [
        "Concept Explainer",
        "Smart Note Generator",
        "Doubt Solver",
        "Quiz Generator",
        "Text Summarizer",
    ])

    language = st.selectbox("✦ Language", [
        "English",
        "Tamil",
        "Hindi",
    ])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 1rem; background: rgba(99,102,241,0.08); border-radius: 10px; border: 1px solid rgba(99,102,241,0.15);">
        <p style="font-size: 0.75rem; color: rgba(148,163,184,0.7); line-height: 1.6;">
            Built for non-tier-1 students who deserve world-class learning tools. 🚀
        </p>
    </div>
    """, unsafe_allow_html=True)

# Feature headers config
headers = {
    "Concept Explainer":    ("Concept Explainer",    "Break down any topic — simply and clearly."),
    "Smart Note Generator": ("Smart Note Generator", "Structured notes for any subject, instantly."),
    "Doubt Solver":         ("Doubt Solver",          "Ask anything. Get a clear, direct answer."),
    "Quiz Generator":       ("Quiz Generator",        "Test your knowledge with auto-generated MCQs."),
    "Text Summarizer":      ("Text Summarizer",       "Paste any text — get the key points fast."),
}

title, subtitle = headers[feature]
st.markdown(f"""
<div class="page-header">
    <h2>{title}</h2>
    <p>{subtitle}</p>
</div>
""", unsafe_allow_html=True)

# Features
if feature == "Concept Explainer":
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        topic = st.text_input("Topic", placeholder="e.g. Transformer architecture, Dijkstra's algorithm...")
        level = st.selectbox("Your level", ["Beginner", "Intermediate", "Advanced"])
        clicked = st.button("Explain →")
        st.markdown('</div>', unsafe_allow_html=True)

        if clicked:
            if topic:
                with st.spinner("Thinking..."):
                    prompt = f"Explain '{topic}' for a {level} college student clearly and thoroughly. Respond in {language}."
                    result = get_response(prompt)
                st.markdown(f'<div class="result-card">{result}</div>', unsafe_allow_html=True)
            else:
                st.warning("Enter a topic first!")

elif feature == "Smart Note Generator":
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        subject = st.text_input("Subject", placeholder="e.g. Operating Systems, Data Structures...")
        clicked = st.button("Generate Notes →")
        st.markdown('</div>', unsafe_allow_html=True)

        if clicked:
            if subject:
                with st.spinner("Generating notes..."):
                    prompt = f"Generate structured, detailed study notes for '{subject}' for college students. Use clear headings and bullet points. Respond in {language}."
                    result = get_response(prompt)
                st.markdown(f'<div class="result-card">{result}</div>', unsafe_allow_html=True)
            else:
                st.warning("Enter a subject first!")

elif feature == "Doubt Solver":
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        doubt = st.text_area("Your doubt", placeholder="Type your question here...", height=120)
        clicked = st.button("Solve →")
        st.markdown('</div>', unsafe_allow_html=True)

        if clicked:
            if doubt:
                with st.spinner("Solving..."):
                    prompt = f"Answer this college student's doubt clearly and thoroughly: {doubt}. Respond in {language}."
                    result = get_response(prompt)
                st.markdown(f'<div class="result-card">{result}</div>', unsafe_allow_html=True)
            else:
                st.warning("Type your doubt first!")

elif feature == "Quiz Generator":
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        topic = st.text_input("Topic", placeholder="e.g. Python basics, Linked Lists...")
        num = st.slider("Number of questions", 3, 10, 5)
        clicked = st.button("Generate Quiz →")
        st.markdown('</div>', unsafe_allow_html=True)

        if clicked:
            if topic:
                with st.spinner("Generating quiz..."):
                    prompt = f"Generate {num} MCQ questions with 4 options (A/B/C/D) and correct answers for '{topic}'. Format clearly. Respond in {language}."
                    result = get_response(prompt)
                st.markdown(f'<div class="result-card">{result}</div>', unsafe_allow_html=True)
            else:
                st.warning("Enter a topic first!")

elif feature == "Text Summarizer":
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        text = st.text_area("Paste your text", placeholder="Paste any paragraph, chapter, or notes here...", height=180)
        clicked = st.button("Summarize →")
        st.markdown('</div>', unsafe_allow_html=True)

        if clicked:
            if text:
                with st.spinner("Summarizing..."):
                    prompt = f"Summarize this text concisely for a college student, highlighting key points: {text}. Respond in {language}."
                    result = get_response(prompt)
                st.markdown(f'<div class="result-card">{result}</div>', unsafe_allow_html=True)
            else:
                st.warning("Paste some text first!")
