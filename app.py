from flask import Flask, render_template, request, redirect, url_for
import os
from src.extractor import extract_text_from_pdf, extract_resume_info

# Initialize Flask app
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

        # Extract text from the uploaded PDF
        resume_text = extract_text_from_pdf(file_path)  
        extracted_info = extract_resume_info(resume_text)  

        return render_template("results.html", resume_text=resume_text, extracted_info=extracted_info)

if __name__ == "__main__":
    app.run(debug=True)
