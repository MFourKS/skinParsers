from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
from loguru import logger
import json
import random


async def main(parsed):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    async with webdriver.Chrome(options=options) as driver:
        for parsed_item in parsed.values():
            id = parsed_item.get("id")
            await driver.get(f'https://www.dermis.net/dermisroot/en/{id}/diagnose.htm', wait_load=True)
            await driver.sleep(3)
            parsed_item['images'] = []
            parsed_photoes = await driver.find_elements(By.CSS_SELECTOR, 'img')
            parsed_photoes = [await i.get_attribute('src') for i in parsed_photoes]
            parsed_item['images'] = parsed_photoes
            with open('dermis.json', 'w') as file:
                json.dump(parsed, file, indent=4)
                logger.info('Parsed data saved to file')
    
            
                



if __name__ == '__main__':
    with open('dermis.json', 'r') as file:
        ready_data = json.load(file)
    asyncio.run(main(ready_data))