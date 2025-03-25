from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
import json
from loguru import logger

BASE_URL = "https://www.globalskinatlas.com/diagnosis_search?diag=&site=&morpho="

async def scroll_page(driver):
    scroll_pause_time = 2 
    last_height = await driver.execute_script("return document.body.scrollHeight")
    
    while True:
        await driver.execute_script("window.scrollBy(0, 1000);") 
        await driver.sleep(scroll_pause_time)
        
        new_height = await driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

async def get_case_data(driver):
    data = []
    case_elements = await driver.find_elements(By.CSS_SELECTOR, "div.col-sm-4 div.recent-section")
    
    for case in case_elements:
        try:
            name_elem = await case.find_element(By.CSS_SELECTOR, "center a")
            name = await name_elem.text

            description_link = await name_elem.get_attribute("href")
            
            img_elem = await case.find_element(By.CSS_SELECTOR, "img.image")
            photo_url = await img_elem.get_attribute("src")
            
            data.append({
                "name": name,
                "description": description_link,
                "photo": photo_url
            })
        except Exception as e:
            logger.error(f"Ошибка при извлечении данных с элемента: {e}")
    
    return data

async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        await driver.get(BASE_URL, wait_load=False)  
        await driver.sleep(7)

        await scroll_page(driver)

        all_data = await get_case_data(driver)

        with open('globalskinatlas_data.json', 'w', encoding='utf-8') as file:
            json.dump(all_data, file, indent=4, ensure_ascii=False)
            logger.info('Данные сохранены в globalskinatlas_data.json')

if __name__ == '__main__':
    asyncio.run(main())
