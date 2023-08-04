import os
import base64
import io
from PyPDF2 import PdfReader
from flask import Flask, request, jsonify
import fitz
import logging

#log 관련 설정
if not os.path.isdir('logs'):
    os.mkdir('logs')
#logging.getLogger('werkzeug').disabled = True
logging.basicConfig(filename = "logs/server.log", level = logging.DEBUG
                # , datefmt = '%Y/%m/%d %H:%M:%S %p'  # 년/월/일 시(12시간단위)/분/초 PM/AM
                , datefmt = '%Y/%m/%d %H:%M:%S'  # 년/월/일 시(24시간단위)/분/초
                , format = '%(asctime)s:%(levelname)s:%(message)s')

app = Flask(__name__)

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
    # file_data = request.get_data()
    # print(file_data)
    # if not file_data:
    #     return jsonify({"error":1,"message": "No file data in the request"}), 400

    file_name = request.json.get("file_name")
    print(file_name)
    if not file_name or not file_name.lower().endswith(".pdf"):
        return jsonify({"error": 1,"message":"Invalid file name or format. Only PDF files are supported"}), 400

    # file_path = os.path.join("uploads", file_name)
    # with open(file_path, "wb") as file:
    #     file.write(file_data)
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

    return jsonify({
        "error": 0,
        "message": "File received and saved successfully.",
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
    app.run(host="0.0.0.0", port=PORT, debug=True)
    app.logger.info("Server On :: PORT="+str(PORT))