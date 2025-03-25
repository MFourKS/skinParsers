import requests
import json
import os
import pathlib
from loguru import logger

if __name__ == '__main__':
    parent_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'parsed_photoes')
    parent_dir = os.path.join(parent_dir, 'dermnetnz')
    with open('dermnetnz.json', 'r') as file:
        ready_data = json.load(file)
    for url, value in ready_data.items():
        diagnosis_forlder = os.path.join(parent_dir, value['name'])
        os.makedirs(diagnosis_forlder, exist_ok=True)
        for image_url in value['images']:
            image_name = image_url.split('/')[-2] + image_url.split('/')[-1] 
            if os.path.exists(os.path.join(diagnosis_forlder, image_name)):
                logger.info(f'Пропускаю {image_name}')
                continue
            response = requests.get(image_url)
            if response.status_code == 200:
                logger.info(f'download {os.path.join(diagnosis_forlder, image_name)}')
                with open(os.path.join(diagnosis_forlder, image_name), "wb") as f:
                    f.write(response.content)
            else:
                logger.error(f'Error download {image_url}')
