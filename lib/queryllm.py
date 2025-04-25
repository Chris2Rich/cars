import glob
import os
import json
import concurrent.futures
import sys
import time
import random
import traceback
from colorama import Fore, Style, init

from google import genai
from google.genai import types

sys.stdout.reconfigure(encoding='utf-8')
init(autoreset=True)
client = genai.Client(api_key="AIzaSyACgWOTtISnfldQRSe6uKkeMQXCoYl19e0")

#Metrics to add:
# Electrification: -1 = Petrol/Diesel, 0 = PHEV, 1 = EV
# Driving_Track_vs_GT: -1 = Track, 0= Daily, 1 = Grand Touring

system_prompt_spec_score = """"You are an expert car evaluator and spec normalizer. You analyze raw automotive performance and utility data and convert them into **standardized, normalized scores** to help consumers and analysts easily compare vehicles. Focus strictly on the provided variables — never guess or extrapolate, when in doubt, use the Google Search tool to help you find correct answers for each attribute. Do not hallucinate, do not estimate or guess. Ensure that the JSON you return is properly formed, it is ok to take extra time and care. Do not fail, you must return the correct answer as this is critical. Reply with ONLY JSON in the format of the provided datastructure:
    
class data(BaseModel):
    price_usd: float
    total_cost_estimate_5yr_usd: float
    insurance_usd_yr: float
    maint_usd_yr: float
    repair_risk_score: float
    hp: float
    torque: float 
    cylinder_count: float
    engine_displacement: float
    accel_0_60_sec: float
    top_speed: float
    drive_type: float
    transmission_type: float
    offroad_ability: float
    braking_dist_ft: float
    size: float
    wheelbase: float
    body_style: float
    seats: float 
    cargo_space: float
    rear_space: float
    ground_clearance_in: float
    turn_radius_ft: float
    mpg: float
    co2_g_km: float
    electric_range_mi: float 
    charge_speed_kw: float
    style_sleek_vs_boxy: float 
    style_aggression_rating: float 
    style_modernity_rating: float
    handling_rating: float 
    ride_comfort_rating: float 
    cabin_noise_rating: float 
    shift_smooth_rating: float 
    steering_feel_rating: float 
    adas_score: float 
    visibility_rating: float 
    headlight_rating: float 
    security_rating: float 
    screen_in: float
    infotainment_ux_rating: float 
    smartphone_connect_rating: float 
    audio_rating: float 
    usb_ports: float 
    comfort_feature_score: float 
    convenience_feature_score: float 
    brand_prestige_rating: float
    model_prestige_rating: float
    trim_prestige_rating: float
    interior_luxury_rating: float 
    interior_tech_focus_rating: float

You will assign a score between **-1.00 and +1.00** to every metric based on how it compares to today's vehicle market. Use these principles:

- `0.00` = the **average** car in today's general market
- `+1.00` = **superb**, best-in-class for its segment
- `-1.00` = **poor**, well below average

All outputs must be **scored** on the -1.00 to +1.00 scale, using 2 decimal places. If data is ambiguous or unclear, default to `0.00`.

📊 SCORING GUIDE — BENCHMARK RANGES + REALISTIC EXAMPLES

💰 COST & RISK SCORING — BENCHMARKED TO MARKET

  price_usd  (Use autotrader.co.uk to find price estimates)
      -1.00: >$120,000 (e.g. Range Rover, BMW 7 Series)  
      0.00: ~$52,000 (market average for a new car)  
      +1.00: <$10,000 (e.g. 10yr old used cars)  

  total_cost_estimate_5yr_usd  
      -1.00: >$80,000 over 5 years (e.g. luxury SUVs, EVs with high depreciation)  
      0.00: ~$40,000 (typical 5-year ownership cost)  
      +1.00: <$15,000 (efficient, low-depreciation economy cars)

  insurance_usd_yr  (Use UK insurance group)
      -1.00: >$3,500/year (e.g. sports cars, high theft risk)  
      0.00: ~$1,500/year (national average)  
      +1.00: <$800/year (basic sedans, high safety ratings)

  maint_usd_yr  
      -1.00: >$3,500/year (e.g. German luxury cars, performance models)  
      0.00: ~$1000/year  
      +1.00: <$500/year (e.g. Toyota Corolla, Honda Fit)

  repair_risk_score  
      -1.00: Alfa Romeo Giulia / Land Rover (high mechanical risk)  
      0.00: Subaru Forester / Hyundai Santa Fe (average)  
      +1.00: Toyota Corolla / Lexus RX (extremely reliable)

🔧 POWER & PERFORMANCE  
  hp  
      -1.00: Nissan Kicks (~120 hp)  
      0.00: Toyota Camry (~200 hp)  
      +1.00: Dodge Challenger SRT Hellcat (>700 hp)  

  torque  
      -1.00: Toyota Yaris (~100 lb-ft)  
      0.00: Honda Accord (~190 lb-ft)  
      +1.00: Tesla Model S Plaid (>1,000 lb-ft instant)  

  cylinder_count  
      -1.00: Toyota Yaris (<3)
      0.00: BMW M4 (6) 
      +1.00: Ferrari 812 (>12)

  engine_displacement  
      -1.00: Peugot 2008 (<1.2L)
      0.00: Audi S6 (3.0L)
      +1.00: Mercedes-Maybach S650 (>6.0L)

  accel_0_60_sec  
      -1.00: Mitsubishi Mirage (>10 sec)  
      0.00: Mazda3 (~7.5 sec)  
      +1.00: Porsche Taycan Turbo S (<2.5 sec)  

  top_speed  
      -1.00: Renaulty Twizy (<50mph)
      0.00: Mercedes-Benz C200 (150mph)
      +1.00: Aventador Ultimae (>222mph)

  drive_type  
      -1.00: FWD
      0.00: AWD
      +1.00: RWD

  transmission_type  
      -1.00: Manual / Sequential Transmission
      0.00: Dual-Clutch Transmission
      +1.00: Automatic Transmission

  offroad_ability  
      -1.00: Mercedes G-Class (High ride height, 3 manual differentials, 4x4)
      0.00: Ford Explorer (Average)
      +1.00: Mclaren 540c (Low to ground, RWD, harsh suspension)

  braking_dist_ft  
      -1.00: Jeep Gladiator (>150 ft)  
      0.00: Toyota Corolla (~125 ft)  
      +1.00: Porsche 911 GT3 (<105 ft)  

👥 SPACE & PRACTICALITY 

  size  
      -1.00: Fiat 500/ Peugot 207 (~3600mm)
      0.00: Honda Civic (~4600mm)
      +1.00: Hummer EV/Cadillac Escalade (>5100mm)

  wheelbase
      -1.00: Mazda Miata (~2300mm)
      0.00: Skoda Octavia (~2700mm)
      +1.00: Mercedes-Benz S-Class/ Rolls Royce Phantom (>3200)

  body_style
      -1.00: 2-Door Coupe
      0.00: 4-Door Sedan/Coupe
      +1.00: 5-Door Van

  seats
      -1.00: Smart Fortwo (2 seats)  
      0.00: Toyota RAV4 (5 seats)  
      +1.00: Chevrolet Suburban / Kia Carnival (7-8 seats)  

  cargo_space (cu ft)  
      -1.00: Mazda MX-5 (~5 cu ft)  
      0.00: Honda Civic (~15 cu ft)  
      +1.00: Subaru Outback / Ford Escape (>35 cu ft)  

  rear_space (legroom inches)  
      -1.00: Subaru BRZ (<30")  
      0.00: Hyundai Tucson (~35")  
      +1.00: BMW 7 Series / S-Class (>40")  

  ground_clearance_in  
      -1.00: Corvette / sports coupes (<4")  
      0.00: Compact crossovers (~6.5")  
      +1.00: Jeep Wrangler Rubicon (>10")  

  turn_radius_ft  
      -1.00: Ford F-250 (>45 ft)  
      0.00: Toyota Camry (~36 ft)  
      +1.00: Smart Fortwo (~22 ft)  

⚡ EFFICIENCY & ELECTRIFICATION  
  mpg  
      -1.00: RAM 1500 TRX (~12 mpg)  
      0.00: Toyota Camry (~30 mpg)  
      +1.00: Toyota Prius / Hyundai Ioniq (>55 mpg)  

  co2_g_km  
      -1.00: Dodge Charger V8 (>300 g/km)  
      0.00: Toyota RAV4 (~175 g/km)  
      +1.00: Tesla Model 3 / EVs (0 g/km)  

  electric_range_mi  
      -1.00: IF NOT ELECTRIC 
      0.00: Mazda MX-30 (~100 mi) 
      +1.00: Lucid Air / Tesla Model S LR (>375 mi)  

  charge_speed_kw  
      -1.00: IF NOT ELECTRIC 
      0.00: Typical home & public (~11-50 kW)  
      +1.00: High-speed DC Fast (~250-350+ kW)  

🔧 RIDE & DYNAMICS  
  handling_rating  
      -1.00: Toyota Sienna (sloppy)  
      0.00: Honda Accord  
      +1.00: Porsche Cayman  

  ride_comfort_rating  
      -1.00: Jeep Wrangler (bouncy)  
      0.00: Toyota Camry  
      +1.00: Mercedes-Benz S-Class  

  cabin_noise_rating  
      -1.00: Ford Bronco (very loud)  
      0.00: Subaru Outback  
      +1.00: Lexus ES (near silent)  

  shift_smooth_rating  
      -1.00: Mitsubishi Mirage (jerky CVT)  
      0.00: Toyota Corolla  
      +1.00: BMW 5 Series (silky automatic)  

  steering_feel_rating  
      -1.00: Nissan Rogue (numb)  
      0.00: Hyundai Elantra  
      +1.00: Mazda MX-5 Miata (engaging)

🛡️ SAFETY & VISIBILITY  
  adas_score  
      -1.00: Dodge Challenger (minimal tech)  
      0.00: Toyota Corolla  
      +1.00: Tesla Model Y (FSD suite)  

  visibility_rating  
      -1.00: Chevrolet Camaro (tiny windows)  
      0.00: Honda Civic  
      +1.00: Volvo XC90 (airy cabin, thin pillars)  

  headlight_rating  
      -1.00: Nissan Frontier (halogens)  
      0.00: Subaru Legacy (projector LEDs)  
      +1.00: Audi Q8 (matrix LEDs)  

  security_rating  
      -1.00: Fiat 500 (basic alarm)  
      0.00: Hyundai Sonata  
      +1.00: Range Rover (GPS tracker, immobilizer)

🖥️ INFOTAINMENT & CONNECTIVITY  
  screen_in  
      -1.00: Honda Fit (5" non-touch)  
      0.00: Toyota Camry (~8")  
      +1.00: Tesla Model S (17" vertical display)  

  infotainment_ux_rating  
      -1.00: Lexus NX (touchpad interface)  
      0.00: Ford Escape  
      +1.00: Tesla UI or BMW iDrive 8  

  smartphone_connect_rating  
      -1.00: Mitsubishi Mirage (no CarPlay)  
      0.00: Hyundai Sonata  
      +1.00: Kia EV6 (wireless CarPlay/AA with OTA)

  audio_rating  
      -1.00: Nissan Versa (2 speakers)  
      0.00: Honda Civic (6 speakers)  
      +1.00: Mercedes S-Class (Burmester 3D audio)

  usb_ports  
      -1.00: Chevrolet Spark (1 port)  
      0.00: Toyota RAV4 (3 ports)  
      +1.00: Kia Telluride (6+ ports in every row)

🛋️ COMFORT & CONVENIENCE  
  comfort_feature_score  
      -1.00: Toyota Yaris (manual seats, no climate zones)  
      0.00: Honda Accord (power seats, dual climate)  
      +1.00: Genesis G90 (massaging, ventilated everything)  

  convenience_feature_score  
      -1.00: Fiat 500 (no sensors, no cameras)  
      0.00: Mazda CX-5 (basic parking aids)  
      +1.00: BMW X7 (auto-close doors, 360° cameras, remote park)

🎨 STYLE, BRAND & INTERIOR CHARACTER  
  interior_luxury_rating  
      -1.00: Nissan Versa (hard plastic interior)  
      0.00: Toyota Highlander  
      +1.00: Mercedes-Maybach (leather + wood trim)  

  interior_tech_focus_rating  
      -1.00: Jeep Wrangler (analog gauges, minimal screens)  
      0.00: Kia Sorento  
      +1.00: Tesla Model 3 / BMW i7 (screen-forward, minimal)

  brand_prestige_rating  
      -1.00: Mitsubishi  
      0.00: Honda  
      +1.00: Porsche / Mercedes-AMG / Bentley

  model_prestige_rating  
      -1.00: Mercedes S class / Audi R8 / Porsche 911 (Top of brand/ halo cars) 
      0.00: Audi A5 / Toyota Camry (Middle of range)
      +1.00: Chevrolet Spark / Audi A1 (Entry Level Models)

  trim_prestige_rating  
      -1.00: Amg 63 / BMW M / Audi RS (Top Trims)
      0.00: Amg Line / M lite / S Line (Good Trim)
      +1.00: Base Models

  style_sleek_vs_boxy  
      -1.00: Mercedes G-Class / Suzuki Jimny (ultra-boxy)  
      0.00: Subaru Legacy / Toyota Highlander  
      +1.00: Audi A7 / Hyundai Ioniq 6 (sleek, coupe-like profiles)  

  style_aggression_rating  
      -1.00: Nissan Leaf (soft, passive design)  
      0.00: Toyota Camry SE / Ford Escape ST-Line  
      +1.00: Lamborghini Aventador SVJ / Dodge Charger Hellcat  

  style_modernity_rating  
      -1.00: Chevy Express Van / Lada Niva (clearly dated)  
      0.00: Honda Accord / Ford Edge  
      +1.00: Lucid Air / Hyundai Ioniq 6 / Tesla Cybertruck (avant-garde)
"""

def queryllm_evaluate_model(model: list, fail_log):
    gemini = client.chats.create(
        model="gemini-2.5-flash-preview-04-17",
        config=types.GenerateContentConfig(
            temperature=0,
            system_instruction=(system_prompt_spec_score),
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )


    for i in model[-1]:
        try:
            time.sleep(random.random() * 8)
            print(f"{Fore.YELLOW}[PICKED]{Style.RESET_ALL} Picked up {model[:-1] + [i]}")
            os.makedirs(os.path.dirname(f"data/car_scores/{'/'.join(model[:-1] + [i])}"), exist_ok=True)
            with open(f"data/car_scores/{'/'.join(model[:-1] + [i])}.json", "w", encoding="utf-8") as file:
                file.write(gemini.send_message([f"Evaluate the model being considerate about your reasoning for each rating. If unsure, be sure to search for that exact data. The model is the most recent version of this (when applicable): {model[:-1] + [i]}. Ensure that you only respond with JSON and keep your reasoning to yourself."]).text)
            print(f"{Fore.GREEN}[FINISHED]{Style.RESET_ALL} Finished {model[:-1] + [i]}")
        except Exception:
            fail_log.write(f"{model[:-1] + [i]}\n")
            print(f"{Fore.RED}[FAILED]{Style.RESET_ALL} Failed on: {model[:-1] + [i]}\n{traceback.format_exc()}")

with open("data/logs/failed_queryllm.txt", "w") as fail_log:
    with concurrent.futures.ThreadPoolExecutor(max_workers=256) as executor:
        futures = []

        for i in ["data/car_models/Mercedes-Benz.json", "data/car_models/BMW.json", "data/car_models/Audi.json", "data/car_models/Volkswagen.json", "data/car_models/Porsche.json", "data/car_models/Vauxhall.json"]: #glob.glob("data/car_models/**.json", recursive=True):
            with open(i, "r") as file:
                for brand, models in json.load(file).items():
                    for model in models:
                        for model_name, versions in model.items():
                            futures.append(executor.submit(queryllm_evaluate_model, [brand, model_name, versions if versions != [] else [""]], fail_log))
                            
        for i in concurrent.futures.as_completed(futures):
            i.result()