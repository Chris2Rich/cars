import requests
import json
import re
import time
import re
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

brands = ["Abarth", "AC", "AK", "Alfa Romeo", "Alpine", "Alvis", "Ariel", "Aston Martin", "Audi", "Austin", "BAC", "Beauford", "Bentley", "BMW", "Bramwith", "Bristol", "Bugatti", "Buick", "BYD", "Cadillac", "Caterham", "Chesil", "Chevrolet", "Chrysler", "Citroen", "Corbin", "Corvette", "CUPRA", "Dacia", "Daewoo", "Daihatsu", "Daimler", "Datsun", "Dax", "DFSK", "Dodge", "DS AUTOMOBILES", "E-COBRA", "Ferrari", "Fiat", "Fisker", "Ford", "Gardner Douglas", "Garia", "Genesis", "GMC", "Great Wall", "GWM", "Hillman", "Honda", "Hummer", "Hyundai", "INEOS", "Infiniti", "ISO", "Isuzu", "Iveco", "JAECOO", "Jaguar", "JBA", "Jeep", "Jensen", "KGM", "Kia", "Koenigsegg", "Lada", "Lamborghini", "Lancia", "Land Rover", "Leapmotor", "LEVC", "Lexus", "Leyland", "Lincoln", "Lister", "London Taxis International", "Lotus", "Mahindra", "Marcos", "Maserati", "MAXUS", "Maybach", "Mazda", "McLaren", "Mercedes-Benz", "Mercury", "MG", "Micro", "Microcar", "MINI", "Mitsubishi", "Mitsuoka", "MK", "MOKE", "Morgan", "Morris", "Nardini", "NG", "Nissan", "Noble", "Omoda", "Opel", "Panther", "Perodua", "Peugeot", "Pilgrim", "Plymouth", "Polestar", "Pontiac", "Porsche", "Proton", "Radical", "Ram", "Reliant", "Renault", "Riley", "Robin Hood", "Rolls-Royce", "Rover", "Saab", "SEAT", "Secma", "Shelby", "Skoda", "Skywell", "Smart", "SsangYong", "Studebaker", "Subaru", "Suzuki", "Tesla", "Toyota", "Triumph", "TVR", "Ultima", "Vauxhall", "Volkswagen", "Volvo", "Westfield", "Yamaha", "Zenos"]

data = {i:[] for i in brands}

def scrape_models(make):
    url = f"https://www.autotrader.co.uk/car-search?make={make}&postcode=NG15GA"
    driver = webdriver.Chrome()  # Ensure you have chromedriver installed
    driver.get(url)
    time.sleep(2)  # Allow the page to load

    driver.switch_to.frame(driver.find_element(By.ID, "sp_message_iframe_1086457"))

    reject = driver.find_element(By.XPATH, "//*[@id='notice']/div[4]/button[2]")
    reject.click()

    time.sleep(2)

    driver.switch_to.default_content()
    button = driver.find_element(By.XPATH, "//button[text()='Filter and sort']")
    button.click()

    time.sleep(2)

    button = driver.find_element(By.NAME, "make-and-model-filter")
    button.click()

    time.sleep(1)

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
        data[make].append({selector.options[i].get_attribute("value") : trims})
        
    driver.quit()

headers = {"User-Agent": "CZ (cz07business@gmail.com)"}

for i in brands:
    time.sleep(2)
    scrape_models(i)
file = open(f"data/car_models.json", "w")
file.writelines(json.dumps(data))
file.close()