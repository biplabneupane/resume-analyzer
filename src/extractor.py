import re

def extract_name(text):
    """Basic name extraction (Assumes first word is a name)."""
    return text.split("\n")[0].strip()

def extract_email(text):
    """Extracts first email found in the text."""
    match = re.search(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+", text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    """Extracts phone number (supports multiple formats)."""
    match = re.search(r"\+?\d{1,3}[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{4}", text)
    return match.group(0) if match else "Not found"

def extract_skills(text):
    """Basic skill extraction (Predefined skill list for now)."""
    skills = ["Python", "Java", "C++", "JavaScript", "SQL", "Machine Learning", "Flask", "Django"]
    found_skills = [skill for skill in skills if skill.lower() in text.lower()]
    return found_skills if found_skills else "Not found"

def extract_resume_details(text):
    """Extracts key information from resume text."""
    return {
        "Name": extract_name(text),
        "Email": extract_email(text),
        "Phone": extract_phone(text),
        "Skills": extract_skills(text),
    }
