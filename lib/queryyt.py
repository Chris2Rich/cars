from pytube import YouTube
import requests
import re

def queryyt(model: list):
    response = requests.get("https://www.youtube.com/results?search_query=" + "+".join(model), headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"})
    links = [i.group() for i in re.findall(r"href=\"\/watch[^\"]*\"", response.text)]