from flask import Flask, render_template, request, redirect, url_for
import os
from src.extractor import extract_resume_data  # ✅ Correct function name

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            resume_text = f.read()

        extracted_info = extract_resume_data(resume_text)  # ✅ Use extract_resume_data

        return render_template("results.html", resume_text=resume_text, extracted_info=extracted_info)

if __name__ == "__main__":
    app.run(debug=True)
