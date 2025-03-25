from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
import json
from loguru import logger

async def load_links_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data  

async def get_disease_data(driver, diagnosis_url, diagnose_name):
    await driver.get(diagnosis_url, wait_load=True)
    await driver.sleep(3)
    
    try:
        diagnose = diagnose_name
    except Exception as e:
        logger.warning(f"Не удалось найти диагноз на странице {diagnosis_url}: {e}")
        diagnose = "Не найдено"
    
    try:
        description_elem = await driver.find_element(By.CLASS_NAME, 'text')
        description = (await description_elem.text).strip() 
    except Exception as e:
        logger.warning(f"Не удалось найти описание болезни на странице {diagnosis_url}: {e}")
        description = "Описание не найдено"
    
    image_links = []
    try:
        thumbs_div = await driver.find_element(By.CLASS_NAME, 'thumbs')
        image_elems = await thumbs_div.find_elements(By.TAG_NAME, 'a')
        
        for image_elem in image_elems:
            img_tag = await image_elem.find_element(By.TAG_NAME, 'img')
            img_url = await img_tag.get_attribute('src')
            
            if img_url:
                img_url = img_url.replace("/kartinki/", "/foto/")
                image_links.append(img_url)
    except Exception as e:
        logger.warning(f"Не удалось найти изображения на странице {diagnosis_url}: {e}")
    
    return {"diagnose": diagnose, "description": description, "images": image_links}

async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        all_data = []

        diagnosis_links = await load_links_from_json('skinmaster_links.json')
        
        for entry in diagnosis_links:
            diagnosis_url = entry["url"]
            diagnose_name = entry["name"]
            logger.info(f"Обрабатываю страницу: {diagnosis_url}")
            disease_data = await get_disease_data(driver, diagnosis_url, diagnose_name)
            all_data.append(disease_data)
        
        with open('skinmaster.json', 'w', encoding='utf-8') as file:
            json.dump(all_data, file, indent=4, ensure_ascii=False)
            logger.info('Данные сохранены в skinmaster.json')

if __name__ == '__main__':
    asyncio.run(main())
