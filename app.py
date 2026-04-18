import streamlit as st
import google.generativeai as genai
import os

# Direct API key (temporary fix)
GEMINI_API_KEY = "AIzaSyAc2UZfi2ysIgAq_UtXRh_XgdEhyv0zneU"  # paste your key here
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Page config
st.set_page_config(page_title="Fair Study AI", page_icon="🎓")
st.title("🎓 Fair Study AI")
st.caption("Your unbiased AI-powered learning assistant")

# Sidebar
feature = st.sidebar.selectbox("Choose a Feature", [
    "💡 Concept Explainer",
    "📝 Smart Note Generator",
    "🤖 Doubt Solver",
])

# Feature 1
if feature == "💡 Concept Explainer":
    st.header("💡 Concept Explainer")
    topic = st.text_input("Enter a topic:")
    level = st.selectbox("Your level:", ["Beginner", "Intermediate", "Advanced"])
    if st.button("Explain!"):
        if topic:
            with st.spinner("Thinking..."):
                prompt = f"Explain '{topic}' for a {level} college student clearly."
                response = model.generate_content(prompt)
                st.write(response.text)

# Feature 2
elif feature == "📝 Smart Note Generator":
    st.header("📝 Smart Note Generator")
    subject = st.text_input("Enter subject:")
    if st.button("Generate Notes!"):
        if subject:
            with st.spinner("Generating..."):
                prompt = f"Generate structured study notes for '{subject}' for college students."
                response = model.generate_content(prompt)
                st.write(response.text)

# Feature 3
elif feature == "🤖 Doubt Solver":
    st.header("🤖 Doubt Solver")
    doubt = st.text_area("Type your doubt:")
    if st.button("Solve!"):
        if doubt:
            with st.spinner("Solving..."):
                prompt = f"Answer this college student doubt clearly: {doubt}"
                response = model.generate_content(prompt)
                st.write(response.text)