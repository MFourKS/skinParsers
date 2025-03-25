
from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
from loguru import logger
import json
import random


async def main(ready_data):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    async with webdriver.Chrome(options=options) as driver:
        await driver.get(f'https://dermnetnz.org/images', wait_load=True)
        await driver.sleep(3)
        button = await driver.find_element(By.CSS_SELECTOR, 'button[mode="primary"]')
        await button.click()

        for url, _ in ready_data.items():
            await driver.get(url, wait_load=True)
            await driver.sleep(3)
            ready_data[url]['images'] = []
            for i in range(10):
                links_elems = await driver.find_elements(By.CSS_SELECTOR, "img")
                for link_elem in links_elems:
                    link = await link_elem.get_attribute('src')
                    if '/assets/' in link and link not in ready_data[url]['images'] and (link.endswith('.jpg') or link.endswith('.jpeg')):
                        ready_data[url]['images'].append(link)
                await driver.execute_script(f"window.scrollTo(0, {i}*1000);")
                await driver.sleep(1)
            print('ready_data', url, len(ready_data[url]['images']))
            with open('dermnetnz.json', 'w') as file:
                json.dump(ready_data, file, indent=4)

if __name__ == '__main__':
    with open('dermnetnz.json', 'r') as file:
        ready_data = json.load(file)
    asyncio.run(main(ready_data))