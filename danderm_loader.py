import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def sanitize_filename(name, max_length=100):
    name = "_".join(name.split()).replace("/", "_").replace("\\", "_").replace(":", "_")
    return name[:max_length]  

def download_images(json_file, base_folder="danderm_images", max_retries=3, retry_delay=5):
    os.makedirs(base_folder, exist_ok=True)

    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })

    for entry in data:
        title = sanitize_filename(entry.get("title", "Unknown"))
        image_page_url = entry.get("image")

        diagnose_folder = os.path.join(base_folder, title)
        os.makedirs(diagnose_folder, exist_ok=True)

        if image_page_url:
            for attempt in range(max_retries):
                try:
                    response = session.get(image_page_url)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, "html.parser")
                    img_tag = soup.find("img")
                    if img_tag and "src" in img_tag.attrs:
                        img_url = urljoin(image_page_url, img_tag["src"])
                        
                        image_name = os.path.basename(img_url)
                        image_path = os.path.join(diagnose_folder, image_name)
                        
                        for img_attempt in range(max_retries):
                            try:
                                img_response = session.get(img_url, stream=True)
                                img_response.raise_for_status()
                                
                                with open(image_path, "wb") as file:
                                    for chunk in img_response.iter_content(1024):
                                        file.write(chunk)
                                print(f"Downloaded {image_path}")
                                break 
                            except requests.RequestException as e:
                                print(f"Attempt {img_attempt + 1} failed to download {img_url}: {e}")
                                time.sleep(retry_delay)
                        break  
                    else:
                        print(f"No image found on {image_page_url}")
                        break
                except requests.RequestException as e:
                    print(f"Attempt {attempt + 1} failed to fetch {image_page_url}: {e}")
                    time.sleep(retry_delay)
        else:
            print(f"No image URL found for {title}")

if __name__ == "__main__":
    download_images("danderm.json")
