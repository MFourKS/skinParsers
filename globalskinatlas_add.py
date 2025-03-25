import json
import asyncio
from selenium_driverless import webdriver
from selenium_driverless.types.by import By
from loguru import logger

INPUT_FILE = "globalskinatlas.json"
OUTPUT_FILE = "globalskinatlas_enriched.json"

async def fetch_with_retry(driver, url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            await driver.get(url, wait_load=True)
            await driver.sleep(3)
            return True
        except Exception as e:
            logger.error(f"Попытка {attempt + 1}/{retries} не удалась: {e}")
            await asyncio.sleep(delay)
    return False

async def parse_case_details(driver, url):
    success = await fetch_with_retry(driver, url)
    if not success:
        logger.error(f"Не удалось загрузить страницу {url}")
        return {}
    
    try:
        details = {}
        details_block = await driver.find_element(By.CSS_SELECTOR, "div.col-sm-6")
        
        paragraphs = await details_block.find_elements(By.CSS_SELECTOR, "p")
        for p in paragraphs:
            text = await p.text
            if ":" in text:
                key, value = text.split(":", 1)
                details[key.strip()] = value.strip()
        
        return details
    except Exception as e:
        logger.error(f"Ошибка при парсинге {url}: {e}")
        return {}

async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        
        with open(INPUT_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        enriched_data = []
        semaphore = asyncio.Semaphore(5)
        
        for entry in data:
            async with semaphore:
                logger.info(f"Парсим данные для {entry['description']}")
                details = await parse_case_details(driver, entry["description"])
                
                enriched_entry = {**entry, **details} 
                enriched_data.append(enriched_entry)
                print(enriched_data)
                await asyncio.sleep(2) 
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(enriched_data, file, indent=4, ensure_ascii=False)
            logger.info(f"Данные сохранены в {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
