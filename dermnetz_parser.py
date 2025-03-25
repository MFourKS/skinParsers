
from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
from loguru import logger
import json
import random


async def main():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    async with webdriver.Chrome(options=options) as driver:
        await driver.get(f'https://dermnetnz.org/images', wait_load=True)
        await driver.sleep(3)
        parsed = {}

        button = await driver.find_element(By.CSS_SELECTOR, 'button[mode="primary"]')
        await button.click()

        categories_elem = await driver.find_element(By.XPATH, "//*[text()='Galleries']")
        await categories_elem.click()
        await driver.sleep(3)

        for i in range(15):
            links_elems = await driver.find_elements(By.CSS_SELECTOR, "a")
            print('len', len(links_elems))
            for link_elem in links_elems:
                link = await link_elem.get_attribute('href')
                if 'image' in link:
                    parsed[link] = {'images': [], 'name': link.split('/')[-1]}
            await driver.execute_script(f"window.scrollTo(0, {i}*1000);")
            await driver.sleep(1)

        with open('dermnetnz.json', 'w') as file:
            json.dump(parsed, file, indent=4)
            logger.info('Parsed data saved to file')

            
                



if __name__ == '__main__':
    asyncio.run(main())