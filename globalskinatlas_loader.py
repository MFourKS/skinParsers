import os
import json
import requests

def download_images(json_file, base_folder="globalskinatlas"):
    os.makedirs(base_folder, exist_ok=True)

    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    for entry in data:
        name = entry.get("name", "Unknown").replace(" ", "_")
        image_url = entry.get("photo")

        diagnose_folder = os.path.join(base_folder, name)
        os.makedirs(diagnose_folder, exist_ok=True)

        if image_url:
            image_name = os.path.basename(image_url)
            image_path = os.path.join(diagnose_folder, image_name)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            try:
                response = requests.get(image_url, headers=headers, stream=True)
                response.raise_for_status()

                with open(image_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Downloaded {image_path}")
            except requests.RequestException as e:
                print(f"Failed to download {image_url}: {e}")
        else:
            print(f"No image URL found for {name}")

if __name__ == "__main__":
    download_images("globalskinatlas_data.json")
