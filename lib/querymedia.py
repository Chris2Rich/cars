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

topics = ["comfortable", "useability", "sport", "reliability"]

def queryyt(model: list, topic: str):
    ydl_opts = {
        "quiet": True,
        "extract_flat": False,
        "format": "bestaudio",
        "postprocessors": [
            {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "64",
            }
    ],
        "outtmpl": f"data/car_videos/{(('/'.join(model)) if model[-1] != '' else ('/'.join(model)) + 'base_model')+'/'+topic}/%(autonumber)02d",
    }

    try:
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        ydl.extract_info(f"ytsearch8: {''.join(model)} {topic} review", download=True)
        print(f"Scraped audio {model}")
    except Exception as e:
        print(f"Failed audio {model} {e}")
    return

def queryimages(model: list):
    [os.makedirs(os.path.dirname(f"data/car_pictures/{(('/'.join(model)) if model[-1] != '' else ('/'.join(model)) + 'base_model')}/{i}/"), exist_ok=True) for i in ["front", "side", "rear", "interior"]]
    def queryimages_worker_search(model: list):
        url = "https://www.bing.com/images/search?q=" + "+".join(model)
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        time.sleep(3)

        images = [i.get_attribute("src") for i in driver.find_elements(By.CLASS_NAME, "mimg")]

        driver.quit()
        return images
    
    executor_search = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    futures_search = {executor_search.submit(queryimages_worker_search, (model + [i, "&qft=+filterui:imagesize-custom_1080_1920"])): i for i in ["front", "side", "rear", "interior"]}
    search_results = {}

    concurrent.futures.wait(futures_search.keys())

    for i in concurrent.futures.as_completed(futures_search):
        search_results.update({futures_search[i]: i.result()})

    def queryimages_worker_dl(i):
        for j in range(len(search_results[i])):
            link = search_results[i][j]
            if link == None:
                continue
            if link.startswith("data:image"):
                continue
            data = requests.get(link, stream=True, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"})
            file_path = f"data/car_pictures/{(('/'.join(model)) if model[-1] != '' else ('/'.join(model)) + 'base_model')}/{i}/{j}.{data.headers['Content-Type'].split('/')[-1]}"
            file = open(file_path, "wb")
            for block in data.iter_content(1024):
                if not block:
                    break
                file.write(block)
            file.close()

    executor_dl = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    futures_dl = [executor_dl.submit(queryimages_worker_dl, i) for i in search_results]

    concurrent.futures.wait(futures_dl)

    try:        
        for i in concurrent.futures.as_completed(futures_dl):
            i.result()
        print(f"Scraped images {model}")
    except Exception as e:
        print(f"Failed images {model} {e}")
    return    

for i in brands:
    file = open(f"data/car_models/{i}.json", "r")
    data = json.loads(file.readline())

    for brand, models in data.items():
        for model in models:
            for model_name, versions in model.items():
                executor_yt = concurrent.futures.ThreadPoolExecutor(max_workers=4)
                futures_yt = [executor_yt.submit(queryyt, [i, model_name], j) for j in topics]
                for j in concurrent.futures.as_completed(futures_yt):
                    j.result()
                queryimages([i, model_name])