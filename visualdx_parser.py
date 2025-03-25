from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
import json
import random
import time
import requests
from loguru import logger

PROXIES = [
    ###
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Mobile Safari/537.36"
]
#---------------------------------------------------------------------------------------------
def get_proxy():
    proxy = random.choice(PROXIES)
    return {'http': proxy, 'https': proxy}

def fetch_proxy(url):
    proxy = get_proxy()
    headers = {
        'User-Agent': random.choice(USER_AGENTS)
    }
    response = requests.get(url, headers=headers, proxies=proxy)
    return response.text
#---------------------------------------------------------------------------------------------
async def login(driver, username, password):
    await driver.get('https://www.visualdx.com/visualdx/diagnosis/?moduleId=101&diagnosisId=51907&lang=en_US&usePassword#Differential_Diagnosis_And_Pitfalls', wait_load=True)
    await asyncio.sleep(random.uniform(2, 4))
    elem = await driver.find_element(By.ID, 'j_username')
    await elem.send_keys(username)
    elem = await driver.find_element(By.ID, 'j_password')
    await elem.send_keys(password)
    btn_elem = await driver.find_element(By.ID, 'loginFormSubmit')
    await btn_elem.click()
    await asyncio.sleep(random.uniform(8, 12))

# async def slow_scroll(driver):
#     scroll_height = await driver.execute_script("return document.body.scrollHeight")
#     for i in range(1, 6):
#         await driver.execute_script(f"window.scrollTo(0, {i * scroll_height / 5});")
#         await asyncio.sleep(random.uniform(2, 4))

async def main(NEED_TO_PARSE_PAIRS, parsed):
    username = 'info@pro'
    password = 'pro'
    
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-agent={random.choice(USER_AGENTS)}')
    
    async with webdriver.Chrome(options=options) as driver:
        await login(driver, username, password)
        parsed['cookies'] = await driver.get_cookies()
        
        with open('visualdx.json', 'w') as file:
            json.dump(parsed, file, indent=4)
        
        for pair in NEED_TO_PARSE_PAIRS:
            if str(pair) in parsed:
                continue
            
            diagnosis, module = pair
            url = f'https://www.visualdx.com/visualdx/diagnosis/?diagnosisId={diagnosis}&moduleId={module}#view=images'
            page_content = fetch_proxy(url)
            
            await driver.get(url, wait_load=True)
            await asyncio.sleep(random.uniform(3, 5))
            
            # await slow_scroll(driver)
            
            try:
                diagnosis_name_elem = await driver.find_element(By.CSS_SELECTOR, 'span.active')
                diagnosis_name = await diagnosis_name_elem.text
                
                parsed[str(pair)] = {'name': diagnosis_name, 'images': []}
                
                all_images_elems = await driver.find_elements(By.CSS_SELECTOR, 'figure.item a')
                parsed[str(pair)]['count'] = len(all_images_elems)
                
                for elem in all_images_elems:
                    src = await elem.get_attribute('href')
                    if 'api' in src:
                        parsed[str(pair)]['images'].append(src)
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                
                with open('visualdx.json', 'w') as file:
                    json.dump(parsed, file, indent=4)
                
            except Exception as e:
                logger.error(f'Ошибка при обработке {pair}: {e}')

if __name__ == '__main__':
    with open('visualdx.json', 'r') as file:
        ready_data = json.load(file)
    
    NEED_TO_PARSE_PAIRS = [(51907, 101), (52228, 101)] 
    asyncio.run(main(NEED_TO_PARSE_PAIRS, ready_data))
