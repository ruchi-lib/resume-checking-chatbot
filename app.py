import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000/upload_resume/"

st.set_page_config(page_title="Resume Screening Chatbot", layout="wide")
st.title("📄 Resume Screening Chatbot")

st.sidebar.header("Upload Resume")
uploaded_resume = st.sidebar.file_uploader("Upload a PDF or DOCX resume", type=["pdf", "docx"])

st.sidebar.header("Enter Job Description")
job_description = st.sidebar.text_area("Paste the job description here")

if uploaded_resume and job_description:
    with st.spinner("Processing..."):
        # Send resume to backend
        files = {"file": uploaded_resume.getvalue()}
        response = requests.post(API_URL, files=files)

        if response.status_code == 200:
            data = response.json()
            email = data.get("email", "Not found")
            phone = data.get("phone", "Not found")
            skills = ", ".join(data.get("skills", ["Not found"]))
            named_entities = data.get("named_entities", {})

            # Placeholder for AI matching (Replace with real logic)
            match_score = 85  
            feedback = "Your resume matches well with the job description. Consider adding more relevant keywords."

            st.subheader("🔍 Match Result")
            st.metric(label="Match Percentage", value=f"{match_score}%")
            st.write("### 📌 Feedback")
            st.write(feedback)

            st.subheader("📄 Extracted Resume Information")
            st.write(f"📧 **Email:** {email}")
            st.write(f"📞 **Phone:** {phone}")
            st.write(f"💡 **Skills:** {skills}")

            if named_entities:
                st.write("🏢 **Named Entities (Organizations, Locations, People):**")
                for entity, value in named_entities.items():
                    st.write(f"🔹 **{entity}:** {value}")
        else:
            st.error("Failed to process the resume. Please try again.")

else:
    st.warning("Upload a resume and enter a job description to get started!")
