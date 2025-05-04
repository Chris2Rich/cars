import typing
import glob
import os
import json
import concurrent.futures
import threading
import sys
import time
import random
import traceback
from colorama import Fore, Style, init

from google import genai
from google.genai import types
import google.genai.errors

sys.stdout.reconfigure(encoding='utf-8')
init(autoreset=True)
client = genai.Client(api_key="AIzaSyACgWOTtISnfldQRSe6uKkeMQXCoYl19e0")

system_prompt_spec_score = ""
with open("lib/prompt.txt", "r", encoding="utf-8") as file:
    system_prompt_spec_score = "".join(file.readlines())

data_source = ["data/car_models/Mercedes-Benz.json", "data/car_models/BMW.json", "data/car_models/Audi.json", "data/car_models/Volkswagen.json", "data/car_models/Porsche.json", "data/car_models/Vauxhall.json"]

execution_enabled = threading.Event()
execution_enabled.set()

backoff_timer: threading.Timer | None = None
backoff_lock = threading.Lock()

def schedule_backoff(delay: float):
    global backoff_timer

    with backoff_lock:
        if backoff_timer is not None and backoff_timer.is_alive():
            return

        execution_enabled.clear()
        print(f"{Fore.BLUE}[WAITING]{Style.RESET_ALL} Waiting for: {delay} seconds")

        def end_backoff():
            global backoff_timer
            execution_enabled.set()
            with backoff_lock:
                backoff_timer = None

        backoff_timer = threading.Timer(delay, end_backoff)
        backoff_timer.start()

def send_with_backoff(gemini: genai.chats.Chat, messages: list[str]):
    for attempt in range(1, 5 + 1):
        execution_enabled.wait()
        try:
            response = gemini.send_message(messages)
            return response
        except google.genai.errors.ClientError as rl_exc:
            if rl_exc.code == 429 or rl_exc.code == 503:
                if attempt < 5:
                    delay = min(120, 20 * (2 ** (attempt - 1)))
                    if execution_enabled.is_set():
                        execution_enabled.clear()

                        schedule_backoff(delay)
                    execution_enabled.wait()
                    continue
                raise rl_exc
        except Exception as exc:
            raise exc
    raise Exception("No response")

def queryllm_evaluate_model(model: list[str], fail_log: typing.TextIO):
    execution_enabled.wait()
    time.sleep(1)
    execution_enabled.wait()
    time.sleep(random.random() * 2)
    gemini = client.chats.create(
        model="gemini-2.5-flash-preview-04-17",
        config=types.GenerateContentConfig(
            temperature=0,
            system_instruction=(system_prompt_spec_score),
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )

    for i in model[-1]:
        execution_enabled.wait()
        time.sleep(1)
        execution_enabled.wait()
        time.sleep(random.random() * 0.5)
        try:
            print(f"{Fore.YELLOW}[PICKED]{Style.RESET_ALL} Picked up {model[:-1] + [i]}")
            os.makedirs(os.path.dirname(f"data/car_scores/{'/'.join(model[:-1] + [i])}"), exist_ok=True)

            with open(f"data/car_scores/{'/'.join(model[:-1] + [i])}.json", "w", encoding="utf-8") as file:
                file.write(send_with_backoff(gemini, [f"Evaluate the model being considerate about your reasoning for each rating. If unsure, be sure to search for that exact data. The model is the most recent version of this (when applicable): {model[:-1] + [i]}. Ensure that you only respond with JSON and keep your reasoning to yourself."]).text)
            print(f"{Fore.GREEN}[FINISHED]{Style.RESET_ALL} Finished {model[:-1] + [i]}")
        except Exception:
            fail_log.write(f"{model[:-1] + [i]}\n")
            print(f"{Fore.RED}[FAILED]{Style.RESET_ALL} Failed on: {model[:-1] + [i]}\n{traceback.format_exc()}")

with open("data/logs/failed_queryllm.txt", "w") as fail_log:
    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
        futures = []

        for i in data_source: #glob.glob("data/car_models/**.json", recursive=True):
            with open(i, "r") as file:
                for brand, models in json.load(file).items():
                    for model in models:
                        for model_name, versions in model.items():
                            futures.append(executor.submit(queryllm_evaluate_model, [brand, model_name, versions if versions != [] else [""]], fail_log))
                            
        for i in concurrent.futures.as_completed(futures):
            i.result()