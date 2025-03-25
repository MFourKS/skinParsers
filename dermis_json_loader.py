import os
import pathlib
import json
import requests
from loguru import logger
if __name__ == "__main__":
    parent_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'parsed_photoes')
    parent_dir = os.path.join(parent_dir, 'dermis')
    with open('dermis.json', 'r') as file:
        ready_data = json.load(file)
    for diase in ready_data:
        for src in ready_data[diase]['images']:
            diagnosis_forlder = os.path.join(parent_dir, diase)
            os.makedirs(diagnosis_forlder, exist_ok=True)
            image_name = src.split('/')[-3] + src.split('/')[-1] 
            if image_name in os.listdir(diagnosis_forlder):
                logger.info(f'Фото {image_name} уже скачано ({diase})')
                continue
            response = requests.get(src.replace('100px', '550px'))
            with open(os.path.join(diagnosis_forlder, image_name), "wb") as f:
                f.write(response.content)
            logger.info(f'Скачал {diase} {image_name}')
