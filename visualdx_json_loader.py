import os
import json
import requests
import pathlib 
from PIL import Image
from loguru import logger
from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio

async def login(driver, username, password):
    await driver.get('https://www.visualdx.com/visualdx/myVisualDx?usePassword', wait_load=True)
    await driver.sleep(2)
    elem = await driver.find_element(By.ID, 'j_username')
    await elem.send_keys(username)
    elem = await driver.find_element(By.ID, 'j_password')
    await elem.send_keys(password)
    btn_elem = await driver.find_element(By.ID, 'loginFormSubmit')
    await btn_elem.click()
    await driver.sleep(10)

async def main():
    username = '@gmail.com'
    password = '123'
    proxy = 'http://ps119540:Ybu7z6T8Dw@193.42.112.86:8000'
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")
    while True:
        try:
            async with webdriver.Chrome(options=options) as driver:
                await driver.set_single_proxy(proxy)
                # await login(driver, username=username, password=password)
                # await driver.sleep(2000)
                await driver.sleep(2)
                await login(driver, username, password)
                await driver.sleep(5)
                parent_dir = os.path.join(pathlib.Path(__file__).parent.resolve(), 'parsed_photoes')
                for file in os.listdir('.'):
                    if file.endswith('visualdx.json'):
                        folder_name = os.path.join(parent_dir, file.split('.')[0])
                        with open(file, 'r') as f:
                            data = json.load(f)
                        for key, elem in data.items():
                            if key == 'cookies':
                                continue
                            diagnosis_forlder = os.path.join(folder_name, elem['name'])
                            os.makedirs(diagnosis_forlder, exist_ok=True)
                            for image_url in elem['images']:
                                while True:
                                    image_name = image_url.split('/')[-1].split('?')[0]
                                    image_name = image_name + '.jpeg'
                                    if image_name in os.listdir(diagnosis_forlder):
                                        # logger.info(f'Фото {image_name} уже скачано ({elem["name"]})')
                                        break
                                    await driver.get(image_url, wait_load=True)
                                    await driver.sleep(25) 
                                    image_element = await driver.find_element(By.CSS_SELECTOR, "img")  # Укажите точный селектор
                                    image_base64 = await image_element.screenshot_as_png
                                    with open(os.path.join(diagnosis_forlder, image_name), "wb") as f:
                                        f.write(image_base64)
                                    logger.info(f'Скачано фото {image_url} ({elem["name"]}) {os.path.join(diagnosis_forlder, image_name)}')
                                    break
        except Exception as e:
            logger.error(f"Error occurred {e}")
            await driver.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())