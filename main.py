import re
import spacy
from fastapi import FastAPI, File, UploadFile
import PyPDF2
import docx
from typing import List, Dict

app = FastAPI()

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Load skills from an external file
def load_skills():
    with open("skills.txt", "r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f.readlines()}

SKILLS_LIST = load_skills()

# Extract text from PDF
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# Extract text from DOCX
def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

# Clean extracted text
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

# Extract email
def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None

# Extract phone number
def extract_phone(text):
    match = re.search(r"\b\d{10}\b", text)  # Assumes 10-digit phone number (India format)
    return match.group(0) if match else None

# Extract skills using spaCy NLP
def extract_skills(text):
    doc = nlp(text.lower())
    extracted_skills = set()

    for token in doc:
        if token.text in SKILLS_LIST:
            extracted_skills.add(token.text)

    return list(extracted_skills) if extracted_skills else None

# Extract named entities (like organizations, locations, names)
def extract_named_entities(text):
    doc = nlp(text)
    entities = {ent.label_: ent.text for ent in doc.ents if ent.label_ in ["ORG", "GPE", "PERSON"]}
    return entities if entities else None

# Endpoint to upload and extract resume details
@app.post("/upload_resume/")
def upload_resume(file: UploadFile = File(...)):
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file.file)
    elif file.filename.endswith(".docx"):
        text = extract_text_from_docx(file.file)
    else:
        return {"error": "Unsupported file format. Use PDF or DOCX."}

    if not text:
        return {"error": "Could not extract text from the file."}

    text = clean_text(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    named_entities = extract_named_entities(text)

    return {
        "resume_text": text[:500],  # Limiting response size for debugging
        "email": email,
        "phone": phone,
        "skills": skills,
        "named_entities": named_entities
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
