import base64
import requests
import os
import tkinter as tk
from tkinter import ttk, filedialog

def send_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    file_name = os.path.basename(file_path)
    print("Selected file name:", file_name)

    with open(file_path, "rb") as file:
        base64_encoded_data = base64.b64encode(file.read()).decode("utf-8")

    src_language = src_combobox.get()
    dst_languages = dst_listbox.curselection()  # Get the indices of selected items
    dst_languages = [dst_listbox.get(index) for index in dst_languages]  # Get the language names
    print("DST_LANG:",dst_languages)
    data = {
        "file_data": base64_encoded_data,
        "file_name": file_name,
        "src_language": src_language,
        "dst_language": dst_languages
    }

    url = "http://ccdip.cafe24.com:5050/getPDFInfomation"
    response = requests.post(url, json=data)

    response_data = response.json()
    result_text.delete(1.0, tk.END)  # Clear previous content
    result_text.insert(tk.END, str(response_data))

# Create the main UI window
root = tk.Tk()
root.title("PDF Analyzer")

# Create a Combobox for src_language
src_combobox = ttk.Combobox(root, values=["한국어", "영어", "일어", "프랑스어", "독일어", "중국어"])
src_combobox.set("한국어")
src_combobox.pack(pady=5)

# Create a Listbox for dst_language with multiple selections
dst_languages = ["영어", "일어", "프랑스어", "독일어", "중국어"]
dst_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, exportselection=False)
for language in dst_languages:
    dst_listbox.insert(tk.END, language)
dst_listbox.pack(pady=5)

# Create a button to trigger sending the PDF
send_button = tk.Button(root, text="Select and Send PDF", command=send_pdf)
send_button.pack(pady=10)

# Create a text widget to display the result
result_text = tk.Text(root, wrap=tk.WORD)
result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Start the UI event loop
root.mainloop()