import requests
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def querywiki(model: list):
    os.makedirs(os.path.dirname(f"data/car_wiki/{(('/'.join(model)) if model[-1] != '' else ('/'.join(model)) + 'base_model')}.html"), exist_ok=True)
    try:        
        data = requests.get(f"https://en.wikipedia.org/wiki/{'_'.join(model)}", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"}).content.decode("utf-8")
        if "Wikipedia does not have an article with this exact name." in data:
            pass
        else:
            file = open(f"data/car_wiki/{(('/'.join(model)) if model[-1] != '' else ('/'.join(model)) + 'base_model')}.html", "w", encoding="utf-8")
            file.write(data)
            file.close()
        print(f"Scraped wiki {model}")
    except Exception as e:
        print(f"Failed wiki {model} {e}")
    return    