import json
import time
import requests
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

sys.stdout.reconfigure(encoding='utf-8')

brands = ["Abarth", "AC", "Alfa Romeo", "Alpine", "Ariel", "Aston Martin", "Audi", "Austin", "Bentley", "BMW", "Bugatti", "Buick", "BYD", "Cadillac", "Caterham", "Chevrolet", "Chrysler", "Citroen", "CUPRA", "Dacia", "Daimler", "Dodge", "DS AUTOMOBILES", "Ferrari", "Fiat", "Fisker", "Ford", "Gardner Douglas", "Genesis", "GWM", "Honda", "Hummer", "Hyundai", "INEOS", "Infiniti", "Isuzu", "JAECOO", "Jaguar",  "Jeep", "KGM", "Kia", "Koenigsegg", "Lamborghini", "Lancia", "Land Rover", "Leapmotor", "LEVC", "Lexus", "Lincoln", "London Taxis International", "Lotus", "Maserati", "MAXUS", "Maybach", "Mazda", "McLaren", "Mercedes-Benz", "MG", "Micro", "MINI", "Mitsubishi", "Morgan", "Morris", "Nissan", "Noble", "Omoda", "Peugeot", "Pilgrim", "Plymouth", "Polestar", "Pontiac", "Porsche", "Renault", "Rolls-Royce", "Saab", "SEAT", "Shelby", "Skoda", "Skywell", "Smart", "SsangYong", "Subaru", "Suzuki", "Tesla", "Toyota", "Triumph", "TVR", "Ultima", "Vauxhall", "Volkswagen", "Volvo"]

models = {i:[] for i in brands}
reviews = {i:[] for i in brands}

def scrape_models(make):
    url = f"https://www.autotrader.co.uk/car-search?make={make}&postcode=NG15GA"
    driver = webdriver.Chrome()
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

def scrape_reviews(make):
    url = f"https://www.autotrader.co.uk/content/car-reviews?make={make}&refresh=true"
    driver = webdriver.Chrome()  # Ensure you have chromedriver installed
    driver.get(url)
    time.sleep(2)  # Allow the page to load

    if make not in driver.current_url:
        reviews[make] = []
        driver.quit()
        return

    articles = [requests.get(i.get_attribute("href"), headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"}).text for i in driver.find_elements(By.TAG_NAME, "a") if "car-reviews" in i.get_attribute("href")]
    reviews[make] = (articles)
        
    driver.quit()

for i in brands:
    time.sleep(2)
    try:
        scrape_models(i)
        scrape_reviews(i)
        print(f"Scraped {i}")
    except Exception as e:
        print(f"Failed {i}")
    finally:
        if {"": []} in models[i]:
            models[i].remove({"": []})

        if {"": []} in reviews[i]:
            reviews[i].remove({"": []})

        file = open(f"data/car_models/{i}.json", "w")
        file.writelines(json.dumps({i: models[i]}))
        file.close()

        file = open(f"data/car_reviews/{i}.json", "w")
        file.writelines(json.dumps({i: reviews[i]}))
        file.close()