from pytube import YouTube
import requests
import re

def queryyt(model: list):
    response = requests.get("https://www.youtube.com/results?search_query=" + "+".join(model), headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"})
    links = ["https://www.youtube.com" + i for i in re.findall(r"/watch\?[^\"]*", response.text)]
    print(response.text)

queryyt(["bmw", "m4", "competition", "2025", "review"])