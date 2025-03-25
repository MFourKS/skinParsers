from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
import json
from loguru import logger
import re

BASE_URL = "https://www.atlasdermatologico.com.br"

async def get_disease_links(driver):
    """Извлекает ссылки на страницы болезней и их названия"""
    await driver.get(f"{BASE_URL}/browse.jsf", wait_load=True)
    await driver.sleep(3)
    
    diseases = {}
    disease_elements = await driver.find_elements(By.CSS_SELECTOR, "#j_idt21_list .ui-datalist-item a")
    
    for elem in disease_elements:
        relative_link = await elem.get_attribute("href")
        name_elem = await elem.find_element(By.CSS_SELECTOR, "span[itemprop='name']")
        name = await name_elem.text
        
        disease_url = f"{BASE_URL}{relative_link}" if relative_link.startswith("/") else relative_link
        
        diseases[disease_url] = {"images": [], "name": name}
    
    return diseases

async def get_disease_images(driver, disease_url):
    """Извлекает ссылки на изображения с страницы болезни"""
    await driver.get(disease_url, wait_load=True)
    await driver.sleep(3)
    
    images = []
    image_elements = await driver.find_elements(By.CSS_SELECTOR, "#j_idt24 a.thumbWrapper")
    
    for img_elem in image_elements:
        img_relative_url = await img_elem.get_attribute("href")
        img_url = f"{BASE_URL}/{img_relative_url}" if img_relative_url.startswith("img?") else img_relative_url
        
        description_elem = await img_elem.find_element(By.CSS_SELECTOR, "meta[itemprop='description']")
        description = await description_elem.get_attribute("content")
        
        images.append({"url": img_url, "description": description})
    
    return images

async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        diseases = await get_disease_links(driver)
        
        for disease_url in diseases.keys():
            images = await get_disease_images(driver, disease_url)
            diseases[disease_url]["images"] = images
            logger.info(f"Собрано {len(images)} изображений для {disease_url}")
            
        with open('atlasderm.json', 'w', encoding='utf-8') as file:
            json.dump(diseases, file, indent=4, ensure_ascii=False)
            logger.info('Данные сохранены в atlasderm.json')

if __name__ == '__main__':
    asyncio.run(main())
