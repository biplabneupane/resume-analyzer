import re
import spacy
import spacy.cli
from pdfminer.high_level import extract_text

# -----------------------------------------------------------------------------
# Load spaCy model (download if not present)
# -----------------------------------------------------------------------------
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        print("[DEBUG] spaCy model 'en_core_web_sm' not found. Downloading...")
        spacy.cli.download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()

# -----------------------------------------------------------------------------
# External skill pool (750+ general + technical skills)
# -----------------------------------------------------------------------------
with open("data/skillset.txt", "r", encoding="utf-8") as f:
    SKILL_DATABASE = set([line.strip().lower() for line in f if line.strip()])

# -----------------------------------------------------------------------------
# Extract raw text from PDF
# -----------------------------------------------------------------------------
def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

# -----------------------------------------------------------------------------
# Extract Email
# -----------------------------------------------------------------------------
def extract_email(text):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

# -----------------------------------------------------------------------------
# Extract Phone Number
# -----------------------------------------------------------------------------
def extract_phone(text):
    pattern = r"\+?\d{1,4}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}"
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

# -----------------------------------------------------------------------------
# Extract Name (email + capitalized words logic)
# -----------------------------------------------------------------------------
def extract_name(text, email):
    """
    Final bulletproof name extractor:
    1. Match full name from email against the resume
    2. Look for ALL-CAPS lines with 2–3 words (common in headers)
    3. Use spaCy PERSON NER as fallback (only if it looks reasonable)
    """

    # 1. Email-based name match
    username = email.split('@')[0] if email else ""
    username_clean = re.sub(r'\d+', '', username).lower()

    if username_clean:
        name_parts = re.findall(r"[a-zA-Z]{2,}", username_clean)
        if 1 < len(name_parts) <= 3:
            guessed_name = " ".join([p.capitalize() for p in name_parts])
            if guessed_name.lower() in text.lower():
                return guessed_name

    # 2. All-caps line detection (common in resumes)
    lines = text.splitlines()
    for line in lines:
        if (
            line.strip().isupper()
            and 2 <= len(line.strip().split()) <= 4
            and not re.search(r'curriculum|vitae|resume|declaration', line, re.IGNORECASE)
        ):
            return line.strip().title()

    # 3. Fallback to spaCy NER (with filtering)
    doc = nlp(text)
    person_names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
    for name in person_names:
        if (
            2 <= len(name.split()) <= 4
            and not re.search(r'performance|bug|project|objective|summary', name, re.IGNORECASE)
        ):
            return name.title()

    # 4. Ultimate fallback: clean email username
    return guessed_name if username_clean else "Not Found"



# -----------------------------------------------------------------------------
# Extract Skills using external skill database
# -----------------------------------------------------------------------------
def extract_skills(text):
    found = set()
    lower_text = text.lower()
    for skill in SKILL_DATABASE:
        if skill in lower_text:
            found.add(skill.title())
    return ", ".join(sorted(found)) if found else "Not Found"

# -----------------------------------------------------------------------------
# Extract Education lines
# -----------------------------------------------------------------------------
def extract_education(text):
    keywords = [
        "Bachelor", "Master", "PhD", "B.Sc", "M.Sc", "B.Tech", "M.Tech",
        "Engineering", "Management", "University", "College", "NEB"
    ]
    matches = [line.strip() for line in text.splitlines()
               if any(k.lower() in line.lower() for k in keywords)]
    return ", ".join(matches) if matches else "Not Found"

# -----------------------------------------------------------------------------
# Extract Experience lines around dates
# -----------------------------------------------------------------------------
def extract_experience(text):
    lines = text.splitlines()
    exp_blocks = []
    date_pattern = re.compile(
        r'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)?\s?\d{4})\s?(–|-|to)\s?(Present|\d{4})',
        re.IGNORECASE
    )
    for i, line in enumerate(lines):
        if date_pattern.search(line):
            block = [lines[i].strip()]
            if i > 0: block.insert(0, lines[i-1].strip())
            if i+1 < len(lines): block.append(lines[i+1].strip())
            exp_blocks.append(" | ".join(block))
    return "\n".join(exp_blocks) if exp_blocks else "Not Found"

# -----------------------------------------------------------------------------
# Run All Extractors
# -----------------------------------------------------------------------------
def extract_resume_info(text):
    email = extract_email(text) or ""
    return {
        "name": extract_name(text, email),
        "email": email,
        "phone": extract_phone(text) or "",
        "education": extract_education(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text)
    }
