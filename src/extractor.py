import os
import re
import spacy
import spacy.cli
from pdfminer.high_level import extract_text
from difflib import SequenceMatcher

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


from difflib import SequenceMatcher

def extract_name(text, email):
    """
    Extract full name by matching string phrases in resume to email username.
    Only considers lines that do not contain the email.
    """

    if not email:
        return "Not Found"

    # Step 1: Clean email prefix
    username = email.split('@')[0]
    username_clean = re.sub(r'\d+', '', username).lower()

    # Step 2: Clean resume lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    lines = [line for line in lines if '@' not in line and 'email' not in line.lower()]

    best_name = None
    best_score = 0.0

    for line in lines:
        # Extract words (only letters)
        words = re.findall(r'[A-Za-z]{2,}', line)
        # Consider 2-word and 3-word combinations
        for i in range(len(words) - 1):
            combo_2 = f"{words[i]} {words[i + 1]}"
            joined_2 = (words[i] + words[i + 1]).lower()
            score_2 = SequenceMatcher(None, joined_2, username_clean).ratio()
            if score_2 > best_score:
                best_score = score_2
                best_name = combo_2

            if i + 2 < len(words):
                combo_3 = f"{words[i]} {words[i + 1]} {words[i + 2]}"
                joined_3 = (words[i] + words[i + 1] + words[i + 2]).lower()
                score_3 = SequenceMatcher(None, joined_3, username_clean).ratio()
                if score_3 > best_score:
                    best_score = score_3
                    best_name = combo_3

    if best_name and best_score > 0.5:
        return best_name.title()

    # Fallback: clean guess from email
    email_parts = re.findall(r"[a-zA-Z]{2,}", username_clean)
    return " ".join([p.capitalize() for p in email_parts]) if email_parts else "Not Found"



def extract_skills(text):
    """
    Extracts skills from the resume's 'Skills' section only.
    Matches only against known valid skills in data/skillset.txt.
    """

    skill_file_path = os.path.join("data", "skillset.txt")

    # Load the known curated skill list
    known_skills = set()
    if os.path.exists(skill_file_path):
        with open(skill_file_path, "r", encoding="utf-8") as f:
            known_skills = {line.strip().lower() for line in f if line.strip()}

    # Step 1: Try to isolate the 'Skills' section
    skills_section = ""
    skill_section_match = re.search(r"(Skills|Technical Skills|Skill Set)[^\n]*\n([\s\S]{0,1000})", text, re.IGNORECASE)
    if skill_section_match:
        skills_section = skill_section_match.group(2)

    # Fallback to whole text if section not found
    target_text = skills_section if skills_section else text

    # Step 2: Tokenize and match against known skills
    words = re.findall(r"[A-Za-z][A-Za-z0-9+.#\-]{1,}", target_text)
    found_skills = set()

    for word in words:
        word_clean = word.lower()
        if word_clean in known_skills:
            found_skills.add(word.strip())

    return ", ".join(sorted(found_skills, key=str.lower)) if found_skills else "Not Found"




import re

def extract_education_experience(text):
    """
    Extracts education and experience sections using section headers.
    Falls back to pattern-based methods if headers are missing.
    """
    sections = {
        "education": [],
        "experience": []
    }

    headers = {
        "education": re.compile(r"^\s*education\s*$", re.IGNORECASE),
        "experience": re.compile(r"^\s*experience\s*$", re.IGNORECASE),
    }

    stop_headers = re.compile(
        r"^\s*(skills|projects|certificates|contact|personal\s+info|objective|summary|languages|training|references)\s*$",
        re.IGNORECASE
    )

    current = None
    lines = text.splitlines()

    for line in lines:
        clean = line.strip()
        if not clean:
            continue

        if headers["education"].match(clean):
            current = "education"
            continue
        elif headers["experience"].match(clean):
            current = "experience"
            continue
        elif stop_headers.match(clean):
            current = None
            continue

        if current:
            sections[current].append(clean)

    # Fallback: use keyword/date-based heuristics if no header content found
    if not sections["education"]:
        edu_keywords = ["Bachelor", "Master", "PhD", "University", "College", "NEB", "BBS", "MBS", "BBA", "MBA"]
        sections["education"] = [l.strip() for l in lines if any(k.lower() in l.lower() for k in edu_keywords)]

    if not sections["experience"]:
        date_pattern = re.compile(
            r'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\.?\s?\d{4})\s?(–|-|to)\s?(Present|\d{4})',
            re.IGNORECASE
        )
        for i, line in enumerate(lines):
            if date_pattern.search(line):
                snippet = [line.strip()]
                if i > 0:
                    snippet.insert(0, lines[i-1].strip())
                if i + 1 < len(lines):
                    snippet.append(lines[i+1].strip())
                entry = " | ".join([s for s in snippet if s])
                sections["experience"].append(entry)

    return {
        "education": "\n".join(sections["education"]) if sections["education"] else "Not Found",
        "experience": "\n".join(sections["experience"]) if sections["experience"] else "Not Found"
    }




from datetime import datetime
from dateutil import parser as dparser

def calculate_years_of_experience(text):
    """
    Extracts job duration ranges and calculates total experience in years.
    Works with formats like:
    - Jan 2018 - Feb 2020
    - 2015 - Present
    - Feb, 2021 to Oct 2023
    """

    # Normalize common separators
    text = text.replace("–", "-").replace("—", "-").replace(" to ", " - ")

    # Look for potential ranges
    date_range_pattern = re.compile(
        r"(?P<start>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\.?\s?\d{4})\s*[-]\s*(?P<end>(Present|\d{4}))",
        re.IGNORECASE
    )

    total_months = 0
    now = datetime.today()

    for match in date_range_pattern.finditer(text):
        raw_start = match.group("start").strip()
        raw_end = match.group("end").strip()

        try:
            start = dparser.parse(raw_start, fuzzy=True, default=datetime(2000, 1, 1))
        except:
            continue

        try:
            end = now if "present" in raw_end.lower() else dparser.parse(raw_end, fuzzy=True)
        except:
            continue

        months = (end.year - start.year) * 12 + (end.month - start.month)
        total_months += max(0, months)

    # Convert to years
    total_years = round(total_months / 12, 1)
    return total_years if total_years > 0 else "N/A"






# -----------------------------------------------------------------------------
# Full Resume Info Aggregator
# -----------------------------------------------------------------------------
def extract_resume_info(text):
    email = extract_email(text) or ""
    return {
        "name": extract_name(text, email),
        "email": email,
        "phone": extract_phone(text) or "",
        "education": extract_education(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "years_experience": calculate_years_of_experience(text)
    }
