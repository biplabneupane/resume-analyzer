from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from src.extractor import extract_text_from_pdf, extract_resume_info
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
        # 1. Retrieve job description from form
        job_description = request.form['job_description']
        print("[DEBUG] Job description received:", job_description)

        # 2. Fetch all resumes from DB
        all_rows = fetch_all_resumes()
        # each row is tuple: (id, name, email, phone, education, skills, experience)
        resume_texts = []
        resume_meta  = []
        for row in all_rows:
            resume_id, name, email, phone, education, skills, experience = row
            # 3. Combine relevant fields into one text blob per resume
            text_blob = " ".join([education or "", skills or "", experience or ""])
            resume_texts.append(text_blob)
            resume_meta.append({
                'id': resume_id,
                'name': name,
                'email': email,
                'phone': phone
            })

        # 4. Vectorize with TF‑IDF
        #    First document is the job description, the rest are resumes
        corpus = [job_description] + resume_texts
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(corpus)
        # 5. Compute cosine similarity between job desc (0) and each resume (1..N)
        job_vec = tfidf_matrix[0:1]
        resume_vecs = tfidf_matrix[1:]
        sims = cosine_similarity(job_vec, resume_vecs)[0]

        # 6. Pair each resume's metadata with its similarity score
        results = []
        for meta, score in zip(resume_meta, sims):
            results.append({
                **meta,
                'score': round(float(score), 4)   # four decimals is enough
            })

        # 7. Sort resumes by descending similarity
        results.sort(key=lambda x: x['score'], reverse=True)
        print("[DEBUG] Matching results:", results)

        # 8. Render results template
        return render_template(
            'match_results.html',
            job_description=job_description,
            results=results
        )

    # GET: just show the form
    return render_template('match_form.html')



if __name__ == "__main__":
    app.run(debug=True)
