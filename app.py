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
        return "⏳ Please wait a moment before next request!"
    st.session_state.last_request = current_time
    return get_cached_response(prompt)

# Page config
st.set_page_config(page_title="Fair Study AI", layout="wide")
st.title("Fair Study AI")
st.caption("Your unbiased AI-powered learning assistant")

# Sidebar
feature = st.sidebar.selectbox("Choose a Feature", [
    "Concept Explainer",
    "Smart Note Generator",
    "Doubt Solver",
    "Quiz Generator",
    "Text Summarizer",
])

language = st.sidebar.selectbox("Response Language", [
    "English",
    "Tamil",
    "Hindi",
])

# Features
if feature == "Concept Explainer":
    st.header("Concept Explainer")
    topic = st.text_input("Enter a topic:")
    level = st.selectbox("Your level:", ["Beginner", "Intermediate", "Advanced"])
    if st.button("Explain!"):
        if topic:
            with st.spinner("Thinking..."):
                prompt = f"Explain '{topic}' for a {level} college student clearly. Respond in {language}."
                st.write(get_response(prompt))

elif feature == "Smart Note Generator":
    st.header("Smart Note Generator")
    subject = st.text_input("Enter subject:")
    if st.button("Generate Notes!"):
        if subject:
            with st.spinner("Generating..."):
                prompt = f"Generate structured study notes for '{subject}' for college students. Respond in {language}."
                st.write(get_response(prompt))

elif feature == "Doubt Solver":
    st.header("Doubt Solver")
    doubt = st.text_area("Type your doubt:")
    if st.button("Solve!"):
        if doubt:
            with st.spinner("Solving..."):
                prompt = f"Answer this college student doubt clearly: {doubt}. Respond in {language}."
                st.write(get_response(prompt))

elif feature == "Quiz Generator":
    st.header("Quiz Generator")
    topic = st.text_input("Enter topic for quiz:")
    num = st.slider("Number of questions:", 3, 10, 5)
    if st.button("Generate Quiz!"):
        if topic:
            with st.spinner("Generating quiz..."):
                prompt = f"Generate {num} MCQ questions with 4 options and answers for '{topic}'. Respond in {language}."
                st.write(get_response(prompt))

elif feature == "Text Summarizer":
    st.header("Text Summarizer")
    text = st.text_area("Paste your text here:", height=200)
    if st.button("Summarize!"):
        if text:
            with st.spinner("Summarizing..."):
                prompt = f"Summarize this text for a college student: {text}. Respond in {language}."
                st.write(get_response(prompt))
