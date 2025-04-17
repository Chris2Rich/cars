import glob
import os
import concurrent.futures
import sys

from google import genai
from google.genai import types
from pydantic import BaseModel

sys.stdout.reconfigure(encoding='utf-8')
client = genai.Client(api_key="AIzaSyACgWOTtISnfldQRSe6uKkeMQXCoYl19e0")

class fin_data(BaseModel):
    price_usd: float
    total_cost_estimate_5yr_usd: float
    insurance_usd_yr: float
    maint_usd_yr: float
    repair_risk_score: float 

class img_data(BaseModel):
    style_sleek_vs_boxy: float 
    style_aggression_rating: float 
    style_modernity_rating: float

class aud_data(BaseModel):
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

    interior_luxury_rating: float 
    interior_tech_focus_rating: float 
    brand_prestige_rating: float 

class wiki_data(BaseModel):
    hp: float
    torque: float 
    accel_0_60_sec: float
    braking_dist_ft: float
    seats: float 
    cargo_space: float
    rear_space: float
    ground_clearance_in: float
    turn_radius_ft: float
    mpg: float
    co2_g_km: float
    electric_range_mi: float 
    charge_speed_kw: float

system_prompt_spec_score = """"You are an expert car evaluator and spec normalizer. You analyze raw automotive performance and utility data and convert them into **standardized, normalized scores** to help consumers and analysts easily compare vehicles. Focus strictly on the provided variables — never guess or extrapolate.

You will assign a score between **-1.0000 and +1.0000** to every metric based on how it compares to today's vehicle market. Use these principles:

- `0.0000` = the **average** car in today’s general market
- `+1.0000` = **superb**, best-in-class for its segment
- `-1.0000` = **poor**, well below average

All outputs must be **scored** on the -1.0000 to +1.0000 scale, using four decimal places. If data is ambiguous or unclear, default to `0.0000`.

📊 SCORING GUIDE — BENCHMARK RANGES + REALISTIC EXAMPLES

🔧 POWER & PERFORMANCE  
  hp  
      -1.0000: Nissan Kicks (~120 hp)  
      0.0000: Toyota Camry (~200 hp)  
      +1.0000: Dodge Challenger SRT Hellcat (>700 hp)  

  torque  
      -1.0000: Toyota Yaris (~100 lb-ft)  
      0.0000: Honda Accord (~190 lb-ft)  
      +1.0000: Tesla Model S Plaid (>1,000 lb-ft instant)  

  accel_0_60_sec  
      -1.0000: Mitsubishi Mirage (>10 sec)  
      0.0000: Mazda3 (~7.5 sec)  
      +1.0000: Porsche Taycan Turbo S (<2.5 sec)  
      *(Lower = better)*

  braking_dist_ft  
      -1.0000: Jeep Gladiator (>150 ft)  
      0.0000: Toyota Corolla (~125 ft)  
      +1.0000: Porsche 911 GT3 (<105 ft)  
      *(Lower = better)*

👥 SPACE & PRACTICALITY  
  seats  
      -1.0000: Smart Fortwo (2 seats)  
      0.0000: Toyota RAV4 (5 seats)  
      +1.0000: Chevrolet Suburban / Kia Carnival (7–8 seats)  

  cargo_space (cu ft)  
      -1.0000: Mazda MX-5 (~5 cu ft)  
      0.0000: Honda Civic (~15 cu ft)  
      +1.0000: Subaru Outback / Ford Escape (>35 cu ft)  

  rear_space (legroom inches)  
      -1.0000: Subaru BRZ (<30")  
      0.0000: Hyundai Tucson (~35")  
      +1.0000: BMW 7 Series / S-Class (>40")  

  ground_clearance_in  
      -1.0000: Corvette / sports coupes (<4")  
      0.0000: Compact crossovers (~6.5")  
      +1.0000: Jeep Wrangler Rubicon (>10")  

  turn_radius_ft  
      -1.0000: Ford F-250 (>45 ft)  
      0.0000: Toyota Camry (~36 ft)  
      +1.0000: Smart Fortwo (~22 ft)  
      *(Lower = better)*

⚡ EFFICIENCY & ELECTRIFICATION  
  mpg  
      -1.0000: RAM 1500 TRX (~12 mpg)  
      0.0000: Toyota Camry (~30 mpg)  
      +1.0000: Toyota Prius / Hyundai Ioniq (>55 mpg)  

  co2_g_km  
      -1.0000: Dodge Charger V8 (>300 g/km)  
      0.0000: Toyota RAV4 (~175 g/km)  
      +1.0000: Tesla Model 3 / EVs (0 g/km)  
      *(Lower = better)*

  electric_range_mi  
      -1.0000: Mazda MX-30 (~100 mi)  
      0.0000: Nissan Leaf Plus / VW ID.4 (~225 mi)  
      +1.0000: Lucid Air / Tesla Model S LR (>375 mi)  

  charge_speed_kw  
      -1.0000: Level 1 charging (~3–6 kW)  
      0.0000: Typical home & public L2 (~11–50 kW)  
      +1.0000: High-speed DC Fast (~250–350+ kW)  

🔧 RIDE & DYNAMICS  
  handling_rating  
      -1.0000: Toyota Sienna (sloppy)  
      0.0000: Honda Accord  
      +1.0000: Porsche Cayman  

  ride_comfort_rating  
      -1.0000: Jeep Wrangler (bouncy)  
      0.0000: Toyota Camry  
      +1.0000: Mercedes-Benz S-Class  

  cabin_noise_rating  
      -1.0000: Ford Bronco (very loud)  
      0.0000: Subaru Outback  
      +1.0000: Lexus ES (near silent)  

  shift_smooth_rating  
      -1.0000: Mitsubishi Mirage (jerky CVT)  
      0.0000: Toyota Corolla  
      +1.0000: BMW 5 Series (silky automatic)  

  steering_feel_rating  
      -1.0000: Nissan Rogue (numb)  
      0.0000: Hyundai Elantra  
      +1.0000: Mazda MX-5 Miata (engaging)

🛡️ SAFETY & VISIBILITY  
  adas_score  
      -1.0000: Dodge Challenger (minimal tech)  
      0.0000: Toyota Corolla  
      +1.0000: Tesla Model Y (FSD suite)  

  visibility_rating  
      -1.0000: Chevrolet Camaro (tiny windows)  
      0.0000: Honda Civic  
      +1.0000: Volvo XC90 (airy cabin, thin pillars)  

  headlight_rating  
      -1.0000: Nissan Frontier (halogens)  
      0.0000: Subaru Legacy (projector LEDs)  
      +1.0000: Audi Q8 (matrix LEDs)  

  security_rating  
      -1.0000: Fiat 500 (basic alarm)  
      0.0000: Hyundai Sonata  
      +1.0000: Range Rover (GPS tracker, immobilizer)

🖥️ INFOTAINMENT & CONNECTIVITY  
  screen_in  
      -1.0000: Honda Fit (5" non-touch)  
      0.0000: Toyota Camry (~8")  
      +1.0000: Tesla Model S (17" vertical display)  

  infotainment_ux_rating  
      -1.0000: Lexus NX (touchpad interface)  
      0.0000: Ford Escape  
      +1.0000: Tesla UI or BMW iDrive 8  

  smartphone_connect_rating  
      -1.0000: Mitsubishi Mirage (no CarPlay)  
      0.0000: Hyundai Sonata  
      +1.0000: Kia EV6 (wireless CarPlay/AA with OTA)

  audio_rating  
      -1.0000: Nissan Versa (2 speakers)  
      0.0000: Honda Civic (6 speakers)  
      +1.0000: Mercedes S-Class (Burmester 3D audio)

  usb_ports  
      -1.0000: Chevrolet Spark (1 port)  
      0.0000: Toyota RAV4 (3 ports)  
      +1.0000: Kia Telluride (6+ ports in every row)

🛋️ COMFORT & CONVENIENCE  
  comfort_feature_score  
      -1.0000: Toyota Yaris (manual seats, no climate zones)  
      0.0000: Honda Accord (power seats, dual climate)  
      +1.0000: Genesis G90 (massaging, ventilated everything)  

  convenience_feature_score  
      -1.0000: Fiat 500 (no sensors, no cameras)  
      0.0000: Mazda CX-5 (basic parking aids)  
      +1.0000: BMW X7 (auto-close doors, 360° cameras, remote park)

🎨 STYLE, BRAND & INTERIOR CHARACTER  
  interior_luxury_rating  
      -1.0000: Nissan Versa (hard plastic interior)  
      0.0000: Toyota Highlander  
      +1.0000: Mercedes-Maybach (leather + wood trim)  

  interior_tech_focus_rating  
      -1.0000: Jeep Wrangler (analog gauges, minimal screens)  
      0.0000: Kia Sorento  
      +1.0000: Tesla Model 3 / BMW i7 (screen-forward, minimal)

  brand_prestige_rating  
      -1.0000: Mitsubishi  
      0.0000: Honda  
      +1.0000: Porsche / Mercedes-AMG / Bentley

  style_sleek_vs_boxy  
      -1.0000: Mercedes G-Class / Suzuki Jimny (ultra-boxy)  
      0.0000: Subaru Legacy / Toyota Highlander  
      +1.0000: Audi A7 / Hyundai Ioniq 6 (sleek, coupe-like profiles)  

  style_aggression_rating  
      -1.0000: Nissan Leaf (soft, passive design)  
      0.0000: Toyota Camry SE / Ford Escape ST-Line  
      +1.0000: Lamborghini Aventador SVJ / Dodge Charger Hellcat  

  style_modernity_rating  
      -1.0000: Chevy Express Van / Lada Niva (clearly dated)  
      0.0000: Honda Accord / Ford Edge  
      +1.0000: Lucid Air / Hyundai Ioniq 6 / Tesla Cybertruck (avant-garde)
"""

def get_files(model: list, t: str):
  paths_img = [i for i in glob.glob(f"data/car_pictures/{'/'.join(model)}/**", recursive=True) if ".jpeg" in i]
  paths_aud = [i for i in glob.glob(f"data/car_videos/{'/'.join(model)}/**", recursive=True) if ".mp3" in i]

  def get_file(i):
    try:
      r = client.files.upload(file=i)
      print(f"Uploaded file {i} for {model}")
      return r
    except Exception as e:
      print(f"Failed file {i} for {model}", e)
      return None
  
  res_img, res_aud, res_wiki = ([], [], [])
  
  if t == "img":
    executor_img = concurrent.futures.ThreadPoolExecutor(max_workers=8)
    res_img = list(filter(None, list(executor_img.map(get_file, paths_img))))

  if t == "aud":
    executor_aud = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    res_aud = list(filter(None, list(executor_aud.map(get_file, paths_aud))))
    
  if t == "wiki":
    try:
      res_wiki = [(client.files.upload(file=f"data/car_wiki/{model[0]}/{model[1]}.html"))]
    except Exception as e:
      print(f"Failed wiki for {model}", e)
  print(f"Uploaded {t} files for {model}")
  return [{"file_data": {"file_uri": i.uri}} for i in res_img + res_aud + res_wiki]

def queryllm_evaluate_model(model: list, t: str):
  response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[f"Evaluate the model and explain your reasoning for each rating. If unsure, be sure to search for that exact data. The model is: {model}"] ,#+ get_files(model, t),
    config=types.GenerateContentConfig(
      temperature=0,
      system_instruction=(system_prompt_spec_score if t == "wiki" else system_prompt_aud_score if t == "aud" else system_prompt_img_score),
      tools=[types.Tool(google_search=types.GoogleSearch())],
    #   response_mime_type="application/json",
    #   response_schema=list[img_data if t == "img" else aud_data if t == "aud" else wiki_data]
    )
  )
  return response

try:
  model = ["BMW", "1 Series", "135d", "2024"]
  t = "wiki"
  os.makedirs(os.path.dirname(f"data/car_scores/{'/'.join(model)}/{t}.json"), exist_ok=True)
  file = open(f"data/car_scores/{'/'.join(model)}/{t}.json", "w", encoding="utf-8")
  file.write(queryllm_evaluate_model(model, t).text)
  file.close()
except Exception as e:
  print(e)
  while True:
    pass