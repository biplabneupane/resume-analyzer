from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from src.extractor import extract_text_from_pdf, extract_resume_info

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
        extracted_info = extract_resume_info(resume_text)
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
        print("Received Job Description:", job_description)  # Debug

        # In step 2: compute similarity
        # For now, just return confirmation page
        return render_template('match_results.html', job_description=job_description)

    return render_template('match_form.html')


if __name__ == "__main__":
    app.run(debug=True)
