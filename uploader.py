import os
import requests

# Folder containing your lecture files
folder_path = r"C:\\Users\\zhams\\Downloads\\lectures\\lectures"
upload_url = "http://localhost:8000/upload/"

for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path):  # Ensure it's a file
        with open(file_path, "rb") as f:
            files = {"file": (filename, f)}
            response = requests.post(upload_url, files=files)
            if response.status_code == 200:
                print(f"Uploaded {filename}: {response.json()}")
            else:
                print(f"Failed to upload {filename}: {response.text}")
