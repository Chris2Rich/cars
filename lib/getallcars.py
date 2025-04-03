import json
import time
import requests
import sys
import concurrent.futures

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

sys.stdout.reconfigure(encoding='utf-8')

brands = ["Abarth", "AC", "Alfa Romeo", "Alpine", "Ariel", "Aston Martin", "Audi", "Austin", "Bentley", "BMW", "Bugatti", "Buick", "BYD", "Cadillac", "Caterham", "Chevrolet", "Chrysler", "Citroen", "CUPRA", "Dacia", "Daimler", "Dodge", "DS AUTOMOBILES", "Ferrari", "Fiat", "Fisker", "Ford", "Gardner Douglas", "Genesis", "GWM", "Honda", "Hummer", "Hyundai", "INEOS", "Infiniti", "Isuzu", "JAECOO", "Jaguar",  "Jeep", "KGM", "Kia", "Koenigsegg", "Lamborghini", "Lancia", "Land Rover", "Leapmotor", "LEVC", "Lexus", "Lincoln", "London Taxis International", "Lotus", "Maserati", "MAXUS", "Maybach", "Mazda", "McLaren", "Mercedes-Benz", "MG", "Micro", "MINI", "Mitsubishi", "Morgan", "Morris", "Nissan", "Noble", "Omoda", "Peugeot", "Pilgrim", "Plymouth", "Polestar", "Pontiac", "Porsche", "Renault", "Rolls-Royce", "Saab", "SEAT", "Shelby", "Skoda", "Skywell", "Smart", "SsangYong", "Subaru", "Suzuki", "Tesla", "Toyota", "Triumph", "TVR", "Ultima", "Vauxhall", "Volkswagen", "Volvo"]

def scrape_models(make):
    url = f"https://www.autotrader.co.uk/car-search?make={make}&postcode=NG15GA"

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(2)

    driver.switch_to.frame(driver.find_element(By.ID, "sp_message_iframe_1086457"))

    reject = driver.find_element(By.XPATH, "//*[@id='notice']/div[4]/button[2]")
    reject.click()

    time.sleep(2.5)

    driver.switch_to.default_content()
    button = driver.find_element(By.XPATH, "//button[text()='Filter and sort']")
    button.click()

    time.sleep(2.5)

    button = driver.find_element(By.NAME, "make-and-model-filter")
    button.click()

    time.sleep(1)

    if (driver.find_element(By.ID, "model").is_enabled()):
        selector = Select(driver.find_element(By.ID, "model"))
        for i in range(0,len(selector.options)):
            time.sleep(1)
            selector.select_by_index(i)
            time.sleep(2)
            trim_container = driver.find_element(By.ID, "aggregated_trim")
            trims = []
            if trim_container.is_enabled():
                trim_selector = Select(trim_container).options
                for j in trim_selector:
                    trims.append(j.get_attribute("value"))
            models[make].append({selector.options[i].get_attribute("value") : trims})
    else:
        models[make].append({driver.find_element(By.ID, "model").find_element(By.TAG_NAME, "option").text : [""]})
        
    driver.quit()

def scrape_brand(brand):
    models = {i:[] for i in brands}
    try:
        scrape_models(brand)
        print(f"Scraped models {brand}")
    except Exception as e:
        print(f"Failed models {brand}")
    finally:
        if {"": []} in models[brand]:
            models[brand].remove({"": []})

        if {"": []} in reviews[brand]:
            reviews[brand].remove({"": []})

        file = open(f"data/car_models/{brand}.json", "w")
        file.writelines(json.dumps({brand: models[brand]}))
        file.close()

executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
futures = {executor.submit(scrape_brand, i): i for i in brands}
for i in futures:
    i.result()