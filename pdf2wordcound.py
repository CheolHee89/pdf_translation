import os
import base64
import io
from PyPDF2 import PdfReader
from flask import Flask, request, jsonify
import fitz
import logging
from langdetect import detect
import datetime

def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"

def calculate_language_percentages(text):
    languages = {}
    total_characters = len(text)
    
    for char in text:
        lang = detect_language(char)
        if lang in languages:
            languages[lang] += 1
        else:
            languages[lang] = 1
    
    language_percentages = {lang: (count / total_characters) * 100 for lang, count in languages.items()}
    return language_percentages

#log 관련 설정
def configure_logging():
    log_dir = 'logs'
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    
    today = datetime.date.today()
    log_file_path = os.path.join(log_dir, f'server_{today}.log')
    
    logging.basicConfig(filename=log_file_path, level=logging.DEBUG,
                        datefmt='%Y/%m/%d %H:%M:%S', format='%(asctime)s:%(levelname)s:%(message)s')

app = Flask(__name__)

def quarter_text(pdf_file):
    text = ""
    pdf_document = fitz.open(pdf_file)
    for page_num in range(int(pdf_document.page_count/4)):
        page = pdf_document[page_num]
        text += page.get_text()
    pdf_document.close()
    return text


def count_words(pdf_file):
    word_count = 0
    pdf_document = fitz.open(pdf_file)
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text = page.get_text()
        word_count += len(text.split())
    pdf_document.close()
    return word_count

def count_pictures(pdf_file):
    picture_count = 0
    pdf_document = fitz.open(pdf_file)
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        images = page.get_images(full=True)
        picture_count += len(images)
    pdf_document.close()
    return picture_count

@app.route("/getPDFInfomation", methods=["POST"])
def receive_and_save_pdf():
    app.logger.info(f'[{request.method}] {request.path}')
    file_name = request.json.get("file_name")
    if not file_name or not file_name.lower().endswith(".pdf"):
        return jsonify({"error": 1,"message":"Invalid file name or format. Only PDF files are supported"}), 400

    file_data = request.json.get("file_data")
    if file_data == "":
        return jsonify({"error":1,"message": "No file data in the request"}), 400
    else :
        decoded_data = base64.b64decode(file_data)
        file_path = os.path.join("uploads", file_name)
        with open(file_path, "wb") as file:
            file.write(decoded_data)

    src_language = request.json.get("src_language", "unknown")  # Get the src_language from the JSON data
    if not isinstance(src_language, str):
        return jsonify({"error": 1, "message": "src_language must be a string"}), 400

    dst_language = request.json.get("dst_language", "unknown")  # Get the src_language from the JSON data
    if not isinstance(dst_language, list):
        return jsonify({"error": 1, "message": "dst_language must be a List"}), 400

    word_count = count_words(file_path)
    picture_count = count_pictures(file_path)
    text = quarter_text(file_path)

    # ######## laguage ratio ########## 나중에 고려 성능 이슈상 멀티 쓰레드 필요
    # language_percentages = calculate_language_percentages(text)
    # ## Sort language percentages in descending order
    # sorted_languages = sorted(language_percentages.items(), key=lambda x: x[1], reverse=True)
    # ## Extract the language with the highest percentage
    # highest_language = sorted_languages[0][0]
    # ## Create an array with sorted language percentages and their order
    # sorted_language_results = [{"Language": lang, "Percentage": percentage} for lang, percentage in sorted_languages]

    return jsonify({
        "error": 0,
        "message": "File received and saved successfully.",
        #"language_dectect":sorted_language_results,
        "word_count": word_count,
        "picture_count": picture_count,
        "src_language": src_language,
        "dst_language": dst_language,
        "file_name":file_name
    }), 200

PORT=5050
if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    configure_logging()
    app.run(host="0.0.0.0", port=PORT, debug=False)
    app.logger.info("Server On :: PORT="+str(PORT))