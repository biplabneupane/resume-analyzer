import re
import spacy
from pdfminer.high_level import extract_text

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_email(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def extract_phone(text):
    phone_pattern = r"\+?\d{1,4}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}"
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else None

def extract_name(text, email):
    resume_text = text.replace('\n', ' ')
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', resume_text)
    words = cleaned_text.split()

    # Extract username from email and clean
    username = email.split('@')[0]
    username_clean = re.sub(r'\d+', '', username).lower()

    possible_matches = []
    for i in range(len(words) - 1):
        first = words[i].strip()
        last = words[i + 1].strip()
        full = (first + last).lower()
        if full in username_clean:
            possible_matches.append((first.capitalize(), last.capitalize()))

    # Choose the longest matching name (more likely to be full name)
    if possible_matches:
        return ' '.join(possible_matches[0])

    # Fallback: clean email-based guess
    split_guess = re.findall(r'[a-zA-Z][^A-Z]*', username_clean)
    if len(split_guess) >= 2:
        return ' '.join([part.capitalize() for part in split_guess])
    else:
        return username_clean.capitalize()


def extract_skills(text):
    skills = [
        "Python", "Java", "JavaScript", "C++", "Machine Learning", "AI", "NLP",
        "Flask", "Django", "SQL", "AWS", "MS Office", "Communication", "Teamwork",
        "Event Management", "Problem Solving", "Managerial", "Leadership"
    ]
    found_skills = [skill for skill in skills if skill.lower() in text.lower()]
    return ", ".join(found_skills) if found_skills else "Not Found"

def extract_education(text):
    education_keywords = [
        "Bachelor", "Master", "PhD", "B.Sc", "M.Sc", "B.Tech", "M.Tech",
        "Engineering", "Management", "University", "College", "NEB"
    ]
    matches = []
    lines = text.split("\n")
    for line in lines:
        if any(keyword.lower() in line.lower() for keyword in education_keywords):
            matches.append(line.strip())
    return ", ".join(matches) if matches else "Not Found"

def extract_experience(text):
    experience_list = []
    lines = text.split('\n')
    
    # Regex for date range patterns
    date_pattern = re.compile(r'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\s?\d{4})\s?(–|-|to)\s?(Present|\d{4})', re.IGNORECASE)

    for i, line in enumerate(lines):
        if date_pattern.search(line):
            context = []

            # Include current line and surrounding lines for job details
            context.append(lines[i].strip())
            if i > 0:
                context.insert(0, lines[i-1].strip())
            if i+1 < len(lines):
                context.append(lines[i+1].strip())

            experience_list.append(' | '.join([c for c in context if c]))

    return '\n'.join(experience_list) if experience_list else 'Not Found'

def extract_resume_info(text):
    email = extract_email(text)
    return {
        "name": extract_name(text, email),
        "email": email,
        "phone": extract_phone(text),
        "education": extract_education(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text)
    }
