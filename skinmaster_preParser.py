from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
import json
from loguru import logger

BASE_URL = "https://www.skinmaster.ru"
START_URL = f"{BASE_URL}/contents"

async def get_links_from_page(driver, page_url):
    await driver.get(page_url, wait_load=True)
    await driver.sleep(3)
    
    data = []
    rows = await driver.find_elements(By.CSS_SELECTOR, "tr td p a")
    
    for row in rows:
        try:
            link = await row.get_attribute("href")
            name = await row.text
            data.append({"name": name, "url": link})
        except Exception as e:
            logger.error(f"Ошибка при обработке ссылки: {e}")
    
    return data

async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        all_data = []
        
        logger.info(f"Обрабатываю страницу: {START_URL}")
        page_data = await get_links_from_page(driver, START_URL)
        all_data.extend(page_data)
        
        with open('skinmaster_links.json', 'w', encoding='utf-8') as file:
            json.dump(all_data, file, indent=4, ensure_ascii=False)
            logger.info('Данные сохранены в skinmaster_links.json')

if __name__ == '__main__':
    asyncio.run(main())
