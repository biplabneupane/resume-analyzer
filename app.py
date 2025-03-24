from flask import Flask, render_template, request, redirect, url_for
import os
from src.extractor import extract_resume_data

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return redirect(url_for("index"))

    file = request.files["resume"]
    if file.filename == "":
        return redirect(url_for("index"))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        resume_text = f.read()

    extracted_info = extract_resume_data(resume_text)

    return render_template("results.html", resume_text=resume_text, extracted_info=extracted_info)

if __name__ == "__main__":
    app.run(debug=True)
