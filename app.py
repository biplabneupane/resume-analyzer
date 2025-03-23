import os
from flask import Flask, render_template, request
from src.parser import extract_resume_text
from src.extractor import extract_resume_details  # Import extractor

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return "No file part"

    file = request.files["resume"]
    if file.filename == "":
        return "No selected file"

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    resume_text = extract_resume_text(file_path)  # Get raw text
    extracted_info = extract_resume_details(resume_text)  # Extract details

    return render_template("result.html", resume_text=resume_text, extracted_info=extracted_info)

if __name__ == "__main__":
    app.run(debug=True)
