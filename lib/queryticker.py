import requests
import json
import time
import re
from lxml import etree
import sys

sys.stdout.reconfigure(encoding='utf-8')

file = open("data\\ticker_to_cik.json", "r")
ticker_to_cik = json.load(file)
file.close()

def search_cik(ticker: str) -> list:
    cik = "0" * (10 - len(str(ticker_to_cik[ticker.upper()]["cik"]))) + str(ticker_to_cik[ticker.upper()]["cik"])
    headers = {"User-Agent": "CZ (cz07business@gmail.com)"}
    res = []

    response = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=headers)
    if response.status_code == 200:
        data = response.json()
        res += [{"link": f"https://www.sec.gov/Archives/edgar/data/{cik}/{data.get('filings', {}).get('recent', {}).get('accessionNumber', {})[i].replace('-', '')}/{data.get('filings', {}).get('recent', {}).get('primaryDocument', {})[i]}", "date": data.get("filings", {}).get("recent", {}).get("reportDate", {})[i], "type": data.get("filings", {}).get("recent", {}).get("primaryDocDescription", {})[i]} for i, x in enumerate(data.get("filings", {}).get("recent", {}).get("primaryDocDescription", {})) if "10-K" in x or "10-Q" in x]

    response = requests.get(f"https://data.sec.gov/submissions/CIK{cik}-submissions-001.json", headers=headers)
    if response.status_code == 200:
        data = response.json()
        res += [{"link": f"https://www.sec.gov/Archives/edgar/data/{cik}/{data.get('accessionNumber', {})[i].replace('-', '')}/{data.get('primaryDocument', {})[i]}", "date": data.get("reportDate", {})[i], "type": data.get("primaryDocDescription", {})[i]} for i, x in enumerate(data.get("primaryDocDescription", {})) if "10-K" in x or "10-Q" in x]

    res = list(filter(lambda x: None if x["link"][-1] == "/" else x, res))
    for i in range(len(res)):
        time.sleep(0.2)
        response = requests.get(res[i]["link"], headers=headers)
        if response.status_code == 200:
            res[i].update({"data": re.sub(r" style=\".*?\"", "", response.content.decode("utf-8"), 0, re.MULTILINE)})
            print("Success at downloading file:", i)
        else:
            print("Failure at downloading file:", i)
    return res

res = search_cik("aapl")
print("Done")

print(res[0])