import re
import spacy
from pdfminer.high_level import extract_text

# Load the NLP model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    return extract_text(pdf_path)

def extract_email(text):
    """Extract email from text using regex."""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def extract_phone(text):
    """Extract phone number using regex."""
    phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else None

def extract_name(text):
    """Extracts name using NLP (assumes name appears at the beginning)."""
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_skills(text):
    """Extracts skills from text (simple keyword-based matching)."""
    skills = ["Python", "Java", "JavaScript", "C++", "Machine Learning", "AI", "NLP", "Flask", "Django", "SQL", "AWS"]
    found_skills = [skill for skill in skills if skill.lower() in text.lower()]
    return ", ".join(found_skills) if found_skills else "Not Found"

def extract_education(text):
    """Extract education details using NLP."""
    education_keywords = ["Bachelor", "Master", "PhD", "B.Sc", "M.Sc", "B.Tech", "M.Tech", "Engineering"]
    lines = text.split("\n")
    for line in lines:
        if any(keyword in line for keyword in education_keywords):
            return line.strip()
    return "Not Found"

def extract_experience(text):
    """Extract experience details using regex."""
    exp_pattern = r"(\d+)\s+years?\s+of\s+experience"
    experience = re.findall(exp_pattern, text, re.IGNORECASE)
    return experience[0] + " years" if experience else "Not Found"

def extract_resume_info(text):
    """Extracts all key information from resume text."""
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "education": extract_education(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text)
    }
