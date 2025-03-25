from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
import json
from loguru import logger
import re

BASE_URL = "https://danderm-pdv.is.kkh.dk/atlas/"
SECTIONS = ["Collagen.html", "Tumours.html", "Infectious.html", "Genitopathology.html"]

async def get_disease_data(driver, section_url):
    await driver.get(section_url, wait_load=True)
    await driver.sleep(3)
    
    data = []
    tables = await driver.find_elements(By.CSS_SELECTOR, "table[width='80%']")
    
    for table in tables:
        rows = await table.find_elements(By.TAG_NAME, "tr")
        title = None
        
        for row in rows:
            cols = await row.find_elements(By.TAG_NAME, "td")
            if len(cols) == 2:
                strong_elem = await cols[0].find_elements(By.TAG_NAME, "strong")
                if strong_elem:
                    title = await strong_elem[0].text  # Заголовок
                
                link_elem = await cols[1].find_elements(By.TAG_NAME, "a")
                if link_elem:
                    diagnose = await link_elem[0].text  # Диагноз
                    href = await link_elem[0].get_attribute("href")
                    img_link = href if href.startswith("http") else BASE_URL + href
                    
                    data.append({"title": title, "diagnose": diagnose, "image": img_link})
    
    return data

async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        all_data = []
        
        for section in SECTIONS:
            section_url = BASE_URL + section
            logger.info(f"Обрабатываю раздел: {section_url}")
            section_data = await get_disease_data(driver, section_url)
            all_data.extend(section_data)
            
        with open('danderm.json', 'w', encoding='utf-8') as file:
            json.dump(all_data, file, indent=4, ensure_ascii=False)
            logger.info('Данные сохранены в danderm_pdv_data.json')

if __name__ == '__main__':
    asyncio.run(main())
