from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
import json
from loguru import logger
import re

BASE_URL = "http://www.hellenicdermatlas.com"
START_URL = f"{BASE_URL}/en/search/advancedSearch/0/0/0/1/"

async def get_last_page_number(driver):
    """Находит номер последней страницы в пагинации"""
    await driver.get(START_URL, wait_load=True)
    await driver.sleep(3)
    
    page_elems = await driver.find_elements(By.CSS_SELECTOR, "#paging a#pager")
    page_numbers = []
    
    for elem in page_elems:
        text = await elem.text
        if text.isdigit():
            page_numbers.append(int(text))
    
    return max(page_numbers) if page_numbers else 1

async def get_disease_data(driver, page_url):
    """Извлекает данные о болезнях с одной страницы"""
    await driver.get(page_url, wait_load=True)
    await driver.sleep(3)
    
    data = []
    tables = await driver.find_elements(By.CSS_SELECTOR, "table[style='margin-top: 20px;']")
    
    for table in tables:
        try:
            # Извлекаем ID
            view_link = await table.find_element(By.CSS_SELECTOR, "a[href*='/en/viewpicture/']")
            id_match = re.search(r'/viewpicture/(\d+)/', await view_link.get_attribute("href"))
            if not id_match:
                continue
            obj_id = id_match.group(1)
            
            # Извлекаем категорию
            category_elem = await table.find_element(By.XPATH, ".//td[text()='Category']/following-sibling::td")
            category = await category_elem.text
            
            # Извлекаем диагноз
            diagnose_elem = await table.find_element(By.XPATH, ".//td[text()='Diagnose']/following-sibling::td")
            diagnose = await diagnose_elem.text
            
            data.append({"id": obj_id, "category": category, "diagnose": diagnose})
        except Exception as e:
            logger.error(f"Ошибка при обработке объекта: {e}")
    
    return data

async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        all_data = []
        last_page = await get_last_page_number(driver)
        
        for page_num in range(1, last_page + 1):
            page_url = f"{BASE_URL}/en/search/advancedSearch/0/0/0/{page_num}/"
            logger.info(f"Обрабатываю страницу: {page_url}")
            page_data = await get_disease_data(driver, page_url)
            all_data.extend(page_data)
            
        with open('hellenic.json', 'w', encoding='utf-8') as file:
            json.dump(all_data, file, indent=4, ensure_ascii=False)
            logger.info('Данные сохранены в hellenic.json')

if __name__ == '__main__':
    asyncio.run(main())
