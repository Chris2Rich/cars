import json
import ast
import re 

data_dim = 53
res = []

try:
    with open("data/logs/failed_dataclean.txt", "w") as logs:
        for i in ["data/car_models/Mercedes-Benz.json", "data/car_models/BMW.json", "data/car_models/Audi.json", "data/car_models/Volkswagen.json", "data/car_models/Porsche.json", "data/car_models/Vauxhall.json"]:
            with open(i, "r") as file:
                    for brand, models in json.load(file).items():
                        for model in models:
                            for model_name, versions in model.items():
                                for version in versions:
                                    try:
                                        data = ""
                                        with open(f"data/car_scores/{'/'.join([brand, model_name, version])}.json", "r", encoding="utf-8") as fi:
                                            data = "".join(fi.readlines())
                                        data = re.search(r"(?<=\`{3}json\n)[\w\W]*(?=\n\`{3})", data, re.MULTILINE)
                                        if data:
                                            data = data.group()
                                        else:
                                            logs.write(f"{[brand, model_name, version]}\n")
                                            continue
                                        data = data.replace("[", "").replace("]", "")
                                        try:
                                            tmp = list(ast.literal_eval(data).values())
                                            if len(tmp) == data_dim and (False not in list(map(lambda x: abs(x) <= 1, tmp))):
                                                res.append(tmp)
                                            else:
                                                logs.write(f"{[brand, model_name, version]}\n")
                                                continue
                                        except Exception as e:
                                            logs.write(f"{[brand, model_name, version]}\n")
                                            print([brand, model_name, version], e)
                                    except Exception as e:
                                        logs.write(f"{[brand, model_name, version]}\n")
                                        raise(Exception(e))
    file = open("data/training_data2.txt", "w")
    file.write(str(res))
    file.close()
except Exception as e:
    print(e)