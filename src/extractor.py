import re
import spacy

# Load SpaCy NLP model (make sure to install it using `python -m spacy download en_core_web_sm`)
nlp = spacy.load("en_core_web_sm")

# Predefined list of skills for extraction
SKILLS_LIST = {"Python", "JavaScript", "Machine Learning", "AI", "Data Science", "Docker", "SQL", "AWS", "Flask"}

def extract_contact_info(text):
    """Extract emails and phone numbers from text."""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    return emails, phones

def extract_name(text):
    """Extract name using Named Entity Recognition (NER)."""
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_education(text):
    """Extract degree and university names from text."""
    education_keywords = ["Bachelor", "Master", "PhD", "BSc", "MSc", "BE", "ME"]
    sentences = text.split("\n")
    
    education_info = []
    for sentence in sentences:
        if any(keyword in sentence for keyword in education_keywords):
            education_info.append(sentence.strip())
    
    return education_info

def extract_skills(text):
    """Extract skills from text by checking predefined list."""
    found_skills = set()
    words = set(text.split())
    
    for skill in SKILLS_LIST:
        if skill in words:
            found_skills.add(skill)
    
    return list(found_skills)

def extract_experience(text):
    """Extract experience-related details such as job titles and company names."""
    job_titles = ["Software Engineer", "Data Scientist", "Research Assistant", "Project Manager"]
    sentences = text.split("\n")
    
    experience_info = []
    for sentence in sentences:
        if any(title in sentence for title in job_titles):
            experience_info.append(sentence.strip())
    
    return experience_info

def extract_resume_data(text):
    """Main function to extract all details from a resume."""
    name = extract_name(text)
    emails, phones = extract_contact_info(text)
    education = extract_education(text)
    skills = extract_skills(text)
    experience = extract_experience(text)
    
    return {
        "name": name,
        "emails": emails,
        "phones": phones,
        "education": education,
        "skills": skills,
        "experience": experience
    }
