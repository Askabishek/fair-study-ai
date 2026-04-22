import streamlit as st
from groq import Groq
import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(xai-yKNdDwUoxIsGDRbPKfyjCQLa72gLgjPRz8sw2MddQVzWvU1fB40lxu7DaunQZK2jawvU3VFURKA4KZDD)

st.set_page_config(page_title="Fair Study AI")
st.title("Fair Study AI")
st.caption("Your unbiased AI-powered learning assistant")

feature = st.sidebar.selectbox("Choose a Feature", [
    "Concept Explainer",
    "Smart Note Generator",
    "Doubt Solver",
])

if feature == "Concept Explainer":
    st.header("Concept Explainer")
    topic = st.text_input("Enter a topic:")
    level = st.selectbox("Your level:", ["Beginner", "Intermediate", "Advanced"])
    if st.button("Explain!"):
        if topic:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": f"Explain '{topic}' for a {level} college student clearly."}]
                )
                st.write(response.choices[0].message.content)

elif feature == "Smart Note Generator":
    st.header("Smart Note Generator")
    subject = st.text_input("Enter subject:")
    if st.button("Generate Notes!"):
        if subject:
            with st.spinner("Generating..."):
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": f"Generate structured study notes for '{subject}' for college students."}]
                )
                st.write(response.choices[0].message.content)

elif feature == "Doubt Solver":
    st.header("Doubt Solver")
    doubt = st.text_area("Type your doubt:")
    if st.button("Solve!"):
        if doubt:
            with st.spinner("Solving..."):
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": f"Answer this college student doubt clearly: {doubt}"}]
                )
                st.write(response.choices[0].message.content)
