import time
import base64
import concurrent.futures
import re
import os
import requests
import json

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
        url = "https://www.bing.com/images/search?q=" + "+".join(model)
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        time.sleep(3)

        images = [i.get_attribute("src") for i in driver.find_elements(By.CLASS_NAME, "mimg")]

        driver.quit()
        return images
    
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
    futures = {executor.submit(queryimages_worker, (model + [i, "&qft=+filterui:imagesize-custom_1080_1920"])): i for i in ["front", "side", "rear", "interior"]}
    
    try:
        for i in futures:
            res[futures[i]] = i.result()
            
            for j in range(len(res[futures[i]])):
                link = (res[futures[i]][j])
                if link == None:
                    continue
                if link.startswith("data:image"):
                    continue
                data = requests.get(link, stream=True)
                file_path = f"data/car_pictures/{'/'.join(model)}/{j}.{data.headers['Content-Type'].split('/')[-1]}"
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file = open(file_path, "wb")
                for block in data.iter_content(1024):
                    if not block:
                        break
                    file.write(block)
                file.close()
        print(f"Scraped images {model}")
    except Exception as e:
        print(f"Failed images {model} {e}")
    return    

# queryyt(["bmw", "m4", "competition", "2025", "review"])

queryimages(["bmw", "m4", "competition", "2025"])