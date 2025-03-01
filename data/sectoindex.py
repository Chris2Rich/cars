import json

file = open("data\\rawsec.json", "r")
data = json.load(file)
file.close()

res = {data[i]["ticker"] : {"cik" : data[i]["cik_str"], "name" : data[i]["title"]} for i in data}

file = open("data\\ticker_to_cik.json", "w")
json.dump(res, file)
file.close()