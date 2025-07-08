import re
import spacy
import spacy.cli
from pdfminer.high_level import extract_text

# -----------------------------------------------------------------------------
# Ensure the spaCy model is present; download if missing
# -----------------------------------------------------------------------------
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        print("[DEBUG] spaCy model 'en_core_web_sm' not found. Downloading...")
        spacy.cli.download("en_core_web_sm")
        print("[DEBUG] Download complete. Loading model...")
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()


# -----------------------------------------------------------------------------
# PDF Text Extraction
# -----------------------------------------------------------------------------
def extract_text_from_pdf(pdf_path):
    """
    Extracts raw text from a PDF using pdfminer.
    """
    return extract_text(pdf_path)


# -----------------------------------------------------------------------------
# Basic Field Extractors
# -----------------------------------------------------------------------------
def extract_email(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None


def extract_phone(text):
    phone_pattern = r"\+?\d{1,4}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}"
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else None


def extract_name(text, email):
    """
    Heuristic to infer full name based on email username and text context.
    """
    resume_text = text.replace('\n', ' ')
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', resume_text)
    words = cleaned_text.split()

    # Derive username from email
    username = email.split('@')[0]
    username_clean = re.sub(r'\d+', '', username).lower()

    # Look for consecutive word pairs matching username fragments
    possible = []
    for i in range(len(words) - 1):
        pair = (words[i].strip(), words[i+1].strip())
        full_lower = (pair[0] + pair[1]).lower()
        if full_lower in username_clean:
            possible.append((pair[0].capitalize(), pair[1].capitalize()))

    if possible:
        return ' '.join(possible[0])

    # Fallback: split cleaned username into name parts
    split_guess = re.findall(r'[a-zA-Z][^A-Z]*', username_clean)
    if len(split_guess) >= 2:
        return ' '.join([part.capitalize() for part in split_guess])
    return username_clean.capitalize()


def extract_skills(text):
    skills_list = [
        "Python", "Java", "JavaScript", "C++", "Machine Learning", "AI", "NLP",
        "Flask", "Django", "SQL", "AWS", "MS Office", "Communication", "Teamwork",
        "Event Management", "Problem Solving", "Managerial", "Leadership"
    ]
    found = [s for s in skills_list if s.lower() in text.lower()]
    return ", ".join(found) if found else "Not Found"


def extract_education(text):
    keywords = [
        "Bachelor", "Master", "PhD", "B.Sc", "M.Sc", "B.Tech", "M.Tech",
        "Engineering", "Management", "University", "College", "NEB"
    ]
    matches = [line.strip() for line in text.splitlines()
               if any(k.lower() in line.lower() for k in keywords)]
    return ", ".join(matches) if matches else "Not Found"


def extract_experience(text):
    """
    Extracts lines around date ranges to capture job/experience entries.
    """
    experience_entries = []
    lines = text.splitlines()
    date_pattern = re.compile(
        r'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\s?\d{4})\s?(–|-|to)\s?(Present|\d{4})',
        re.IGNORECASE
    )

    for i, line in enumerate(lines):
        if date_pattern.search(line):
            snippet = [lines[i].strip()]
            if i > 0:
                snippet.insert(0, lines[i-1].strip())
            if i + 1 < len(lines):
                snippet.append(lines[i+1].strip())
            entry = " | ".join([s for s in snippet if s])
            experience_entries.append(entry)

    return "\n".join(experience_entries) if experience_entries else "Not Found"


# -----------------------------------------------------------------------------
# Full Resume Info Aggregator
# -----------------------------------------------------------------------------
def extract_resume_info(text):
    """
    Runs all extractors and returns a dict of parsed fields.
    """
    email = extract_email(text) or ""
    return {
        "name": extract_name(text, email),
        "email": email,
        "phone": extract_phone(text) or "",
        "education": extract_education(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text)
    }
