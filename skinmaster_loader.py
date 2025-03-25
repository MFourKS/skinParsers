import os
import json
import requests

MAX_PATH_LENGTH = 240  # Максимальная длина пути (с учетом имени файла и папки)

MAX_NAME_LENGTH = 100  # Максимальная длина имени папки/файла для безопасной работы

def sanitize_filename(filename):
    # Заменяем недопустимые символы в имени папки
    invalid_chars = [":", "/", "\\", "?", "<", ">", "|", "\"", "«", "»"]
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename

def truncate_name(name, max_length=MAX_NAME_LENGTH):
    # Обрезаем имя, если оно слишком длинное
    if len(name) > max_length:
        name = name[:max_length]
    return name

def get_safe_path(base_folder, diagnose, image_name):
    full_path = os.path.join(base_folder, diagnose, image_name)
    if len(full_path) > MAX_PATH_LENGTH:
        diagnose = diagnose[:50]  
        image_name = image_name[:50]  
        full_path = os.path.join(base_folder, diagnose, image_name)
    return full_path

def download_images(json_file, base_folder="skinmaster"):
    os.makedirs(base_folder, exist_ok=True)
    
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    for entry in data:
        diagnose = entry.get("diagnose", "Unknown").replace(" ", "_")
        diagnose = sanitize_filename(diagnose)  
        diagnose = truncate_name(diagnose)  
        images = entry.get("images", []) 
        
        diagnose_folder = os.path.join(base_folder, diagnose)

        if len(diagnose_folder) > MAX_PATH_LENGTH:
            diagnose_folder = diagnose_folder[:MAX_PATH_LENGTH]  
        os.makedirs(diagnose_folder, exist_ok=True)  
        
        for idx, image_url in enumerate(images):
            image_name = f"{diagnose}_{idx + 1}.jpg"  
            image_name = truncate_name(image_name)  
            image_path = get_safe_path(base_folder, diagnose, image_name)
            
            try:
                if not os.path.exists(os.path.dirname(image_path)):
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)  
                
                response = requests.get(image_url, stream=True)
                response.raise_for_status()  
                
                with open(image_path, "wb") as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)
                print(f"Downloaded {image_path}")
            except requests.RequestException as e:
                print(f"Failed to download {image_url}: {e}")
            except FileNotFoundError as fnf_error:
                print(f"File path error: {fnf_error}")

if __name__ == "__main__":
    download_images("skinmaster.json")
