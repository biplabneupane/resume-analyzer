from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from src.extractor import extract_text_from_pdf, extract_resume_info

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to insert extracted data into the database
def save_to_db(name, email, phone, education, skills, experience):
    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO resumes (name, email, phone, education, skills, experience)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, email, phone, education, skills, experience))

    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return redirect(request.url)

    file = request.files["resume"]
    
    if file.filename == "":
        return redirect(request.url)

    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        resume_text = extract_text_from_pdf(file_path)
        extracted_info = extract_resume_info(resume_text)

        # Extracted fields
        name = extracted_info.get("name", "Unknown")
        email = extracted_info.get("email", "Unknown")
        phone = extracted_info.get("phone", "Unknown")
        education = extracted_info.get("education", "Unknown")
        skills = extracted_info.get("skills", "Unknown")
        experience = extracted_info.get("experience", "Unknown")

        # Save to database
        save_to_db(name, email, phone, education, skills, experience)

        return render_template("results.html", resume_text=resume_text, extracted_info=extracted_info)

if __name__ == "__main__":
    app.run(debug=True)

    
@app.route("/resumes")
def show_resumes():
    conn = sqlite3.connect("resumes.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM resumes")
    resumes = cursor.fetchall()

    conn.close()
    return render_template("search.html", resumes=resumes)

