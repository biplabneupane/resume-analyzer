from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from src.extractor import (
    extract_text_from_pdf,
    extract_name,
    extract_email,
    extract_phone,
    extract_skills,
    extract_education_experience
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = "resumes.db"

def insert_into_db(info):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO resumes (name, email, phone, education, skills, experience)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        info['name'],
        info['email'],
        info['phone'],
        info['education'],
        info['skills'],
        info['experience']
    ))
    conn.commit()
    conn.close()

def fetch_all_resumes():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes")
    rows = cursor.fetchall()
    conn.close()
    return rows

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
        
        # New parsing logic using modular functions
        email = extract_email(resume_text)
        edu_exp = extract_education_experience(resume_text)
        
        extracted_info = {
            "name": extract_name(resume_text, email),
            "email": email,
            "phone": extract_phone(resume_text),
            "education": edu_exp["education"],
            "skills": extract_skills(resume_text),
            "experience": edu_exp["experience"]
        }


        insert_into_db(extracted_info)

        return render_template("results.html", resume_text=resume_text, extracted_info=extracted_info)

@app.route("/resumes")
def show_resumes():
    all_resumes = fetch_all_resumes()
    return render_template("resumes.html", resumes=all_resumes)

@app.route('/match', methods=['GET', 'POST'])
def match_resumes():
    if request.method == 'POST':
        job_description = request.form['job_description']
        print("[DEBUG] Job description received:", job_description)

        all_rows = fetch_all_resumes()
        resume_texts = []
        resume_meta = []

        for row in all_rows:
            resume_id, name, email, phone, education, skills, experience = row
            text_blob = " ".join([education or "", skills or "", experience or ""])
            resume_texts.append(text_blob)
            resume_meta.append({
                'id': resume_id,
                'name': name,
                'email': email,
                'phone': phone,
                'skills': skills or "Not Available"
            })

        corpus = [job_description] + resume_texts
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True,
            strip_accents='unicode'
        )
        tfidf_matrix = vectorizer.fit_transform(corpus)
        job_vec = tfidf_matrix[0:1]
        resume_vecs = tfidf_matrix[1:]

        sims = cosine_similarity(job_vec, resume_vecs)[0]

        results = []
        for meta, score in zip(resume_meta, sims):
            results.append({
                **meta,
                'score': round(float(score), 4)
            })

        results.sort(key=lambda x: x['score'], reverse=True)
        print("[DEBUG] Matching results:", results)

        return render_template(
            'match_results.html',
            job_description=job_description,
            results=results
        )

    return render_template('match_form.html')

if __name__ == "__main__":
    app.run(debug=True)
