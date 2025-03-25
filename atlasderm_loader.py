import os
import json
import requests
import re

def format_image_id(image_id):
    image_id_str = str(image_id).zfill(4)
    return f"0000/{image_id_str}/0000{image_id_str}_standalone.jpg"

def generate_image_url(image_id):
    return f"http://www.hellenicdermatlas.com/photos/{format_image_id(image_id)}"

def sanitize_folder_name(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def download_images(json_file, base_folder="helenicatlas", start_id="375"):
    os.makedirs(base_folder, exist_ok=True)
    
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    start_download = False  # Флаг, чтобы начать загрузку с указанного id
    
    for entry in data:
        image_id = entry.get("id")
        
        if image_id == start_id:
            start_download = True

        if not start_download:
            continue
        
        diagnose = entry.get("diagnose", "Unknown").replace(" ", "_")
        diagnose = sanitize_folder_name(diagnose)
        
        image_url = generate_image_url(image_id)
        
        diagnose_folder = os.path.join(base_folder, diagnose)
        os.makedirs(diagnose_folder, exist_ok=True)
        
        image_path = os.path.join(diagnose_folder, f"{image_id}.jpg")
        

        if os.path.exists(image_path):
            print(f"File {image_path} already exists. Skipping download.")
            continue
        
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            with open(image_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Downloaded {image_path}")
        except requests.RequestException as e:
            print(f"Failed to download {image_url}: {e}")

if __name__ == "__main__":
    start_id = "375" 
    download_images("hellenic_dermatlas.json", start_id=start_id)
