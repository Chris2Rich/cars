import json
import ast
import re 

res = []

try:
    for i in ["data/car_models/Mercedes-Benz.json", "data/car_models/BMW.json", "data/car_models/Audi.json", "data/car_models/Volkswagen.json", "data/car_models/Porsche.json", "data/car_models/Vauxhall.json"]:
        with open(i, "r") as file:
                for brand, models in json.load(file).items():
                    for model in models:
                        if list(model.keys())[0] == "SLK":
                            break
                        for model_name, versions in model.items():
                            for version in versions:
                                try:
                                    fi = open(f"data/car_scores/{'/'.join([brand, model_name, version])}.json", "r", encoding="utf-8")
                                    data = "".join(fi.readlines())
                                    data = re.match(r"json\`\`\`.*\`\`\`")
                                    if data == "":
                                        continue
                                    if data[0] == "[":
                                        fi.seek(0)
                                        data = "".join(fi.readlines()[2:-2]).strip()
                                    fi.close()
                                    try:
                                        res.append(list(ast.literal_eval(data).values()))
                                    except Exception as e:
                                        print([brand, model_name, version], e)
                                except Exception as e:
                                    print([brand, model_name, version])
                                    raise(Exception(e))
    file = open("data/training_data.txt", "w")
    file.write(str(res))
    file.close()
except Exception as e:
    print(e)