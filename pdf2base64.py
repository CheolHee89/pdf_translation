import base64
import requests

# Read the PDF file and encode it to base64
with open("/Users/cheolheelee/Documents/Concorde/test.pdf", "rb") as file:
    base64_encoded_data = base64.b64encode(file.read()).decode("utf-8")

# Write the base64 data to a file
with open("/Users/cheolheelee/Documents/Concorde/base64_encoded_data.txt", "w") as output_file:
    output_file.write(base64_encoded_data)

# Create the data dictionary to be sent in the POST request
data = {
    "file_data": base64_encoded_data,
    "file_name": "test.pdf",
    "src_language": "KR",
    "dst_language": ["EN","JP"]
}

# Send the POST request using the requests library
url = "http://localhost:5050/getPDFInfomation"
response = requests.post(url, json=data)

# Check the response
print(response.json())
