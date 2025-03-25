from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
from loguru import logger
import re
import json



async def main(NEED_TO_PARSE_DIASE):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    async with webdriver.Chrome(options=options) as driver:
        await driver.get('https://www.dermis.net/dermisroot/en/list/all/search.htm', wait_load=True)
        all_a = await driver.find_elements(By.CSS_SELECTOR, 'li a')
        diase_with_id = []
        dease_to_id = {}
        for a in all_a:
            href = await a.get_attribute("href")
            text = await a.text
            text = re.sub(r"\(\d+ images\)", "", text)
            text = re.sub(r"\(\d+ image\)", "", text)
            diase_with_id.append({'href': href, 'text': text.strip()})
            # print(diase_with_id[-1]['text'])
        for now_diase in NEED_TO_PARSE_DIASE:
            for test_diase in diase_with_id:
                if now_diase == test_diase['text']:
                    dease_to_id[now_diase] = {'id': test_diase['href'].split('/')[-2]}
                    break
            else:
                logger.error(f'No match for {now_diase}')
                # pass
        with open('dermis.json', 'w') as file:
            json.dump(dease_to_id, file, indent=4)
            logger.info('Parsed data saved to file')

    
            
                



if __name__ == '__main__':
    with open('dermis.txt', 'r') as file:
        NEED_TO_PARSE_DIASE = file.readlines()
    NEED_TO_PARSE_DIASE = [d.replace('\n', '').strip() for d in NEED_TO_PARSE_DIASE]

    asyncio.run(main(NEED_TO_PARSE_DIASE))