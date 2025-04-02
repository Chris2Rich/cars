import time
import base64
import concurrent.futures
import re
import os

import yt_dlp

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

brands = ["Abarth", "AC", "Alfa Romeo", "Alpine", "Ariel", "Aston Martin", "Audi", "Austin", "Bentley", "BMW", "Bugatti", "Buick", "BYD", "Cadillac", "Caterham", "Chevrolet", "Chrysler", "Citroen", "CUPRA", "Dacia", "Daimler", "Dodge", "DS AUTOMOBILES", "Ferrari", "Fiat", "Fisker", "Ford", "Gardner Douglas", "Genesis", "GWM", "Honda", "Hummer", "Hyundai", "INEOS", "Infiniti", "Isuzu", "JAECOO", "Jaguar",  "Jeep", "KGM", "Kia", "Koenigsegg", "Lamborghini", "Lancia", "Land Rover", "Leapmotor", "LEVC", "Lexus", "Lincoln", "London Taxis International", "Lotus", "Maserati", "MAXUS", "Maybach", "Mazda", "McLaren", "Mercedes-Benz", "MG", "Micro", "MINI", "Mitsubishi", "Morgan", "Morris", "Nissan", "Noble", "Omoda", "Peugeot", "Pilgrim", "Plymouth", "Polestar", "Pontiac", "Porsche", "Renault", "Rolls-Royce", "Saab", "SEAT", "Shelby", "Skoda", "Skywell", "Smart", "SsangYong", "Subaru", "Suzuki", "Tesla", "Toyota", "Triumph", "TVR", "Ultima", "Vauxhall", "Volkswagen", "Volvo"]

def queryyt(model: list):
    ydl_opts = {
        "quiet": True,
        "extract_flat": False,
        "format": "bestaudio",
        "postprocessors": [
            {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
            }
    ],
        "outtmpl": f"data/car_videos/{'_'.join(model)[::-1]}.mp3",
    }

    try:
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        ydl.extract_info("ytsearch5:" + " ".join(model), download=True)
        print(f"Scraped videos {model}")
    except Exception as e:
        print(f"Failed images {model}")
    return

def queryimages(model: list):
    def queryimages_worker(model: list):
        url = "https://www.google.com/search?tbm=isch&q=" + "%20".join(model)
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        
        time.sleep(1)

        reject = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/span/div/div/div/div[3]/div[1]/button[1]/div")
        reject.click()

        time.sleep(3)

        images = [i.get_attribute("src") for i in driver.find_elements(By.CLASS_NAME, "YQ4gaf")]

        driver.quit()

        

        return images
    
    res = {"front": [], "side": [], "rear": []}
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
    futures = {executor.submit(queryimages_worker, (model + [i])): i for i in ["front", "side", "rear"]}
    
    try:
        for i in futures:
            res[futures[i]] = i.result()
            
            for j in range(len(res[futures[i]])):
                data = (res[futures[i]][j])
                extension_regex = r"(?<=data:image\/)[^;]*"
                if re.match(r"https", data):
                    continue

                file_path = f"data/car_pictures/{'/'.join(model)}/{j}.{re.search(extension_regex, data, re.MULTILINE).group()}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file = open(file_path, "w")
                file.write(data.split(",")[1])
                file.close()
        print(f"Scraped images {model}")
    except Exception as e:
        print(f"Failed images {model} {e}")
    return    

# queryyt(["bmw", "m4", "competition", "2025", "review"])

queryimages(["bmw", "m4", "competition", "2025"])