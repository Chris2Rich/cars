import glob
import os
import concurrent.futures

from google import genai
from google.genai import types
from pydantic import BaseModel

client = genai.Client(api_key="AIzaSyACgWOTtISnfldQRSe6uKkeMQXCoYl19e0")

class car_variables(BaseModel):
    price_usd: float
    total_cost_estimate_5yr_usd: float
    mpg: float
    insurance_usd_yr: float
    maint_usd_yr: float
    repair_risk_score: float 

    hp: float
    torque: float 
    accel_0_60_sec: float
    handling_rating: float 
    braking_dist_ft: float 
    ride_comfort_rating: float 
    cabin_noise_rating: float 
    shift_smooth_rating: float 
    steering_feel_rating: float 

    seats: float 
    cargo_space: float
    rear_space: float
    ground_clearance_in: float
    turn_radius_ft: float

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

    reliability_rating: float 
    parts_cost_rating: float 
    dealer_svc_rating: float 

    style_sleek_vs_boxy: float 
    style_aggression_rating: float 
    style_modernity_rating: float 
    interior_luxury_rating: float 
    interior_tech_focus_rating: float 
    brand_prestige_rating: float 

    co2_g_km: float
    electric_range_mi: float 
    charge_speed_kw: float 

system_prompt_car_rate = """"You are an expert car evaluator and sales assistant. You analyze car specifications and translate them into standardized, normalized scores to help buyers make confident, informed choices.
You will be provided with a `car_variables` object. Your job is to assign a score between **-1.0000 and +1.0000** to every *subjective or performance-based* variable, where:

- `0.0000` = the **average** car in today’s general market
- `+1.0000` = **superb**, best-in-class for its category
- `-1.0000` = **poor**, clearly below expectations or outdated

### ⚠️ The following values should not be rated on this scale and must be given as the raw numbers:
- price_usd
- total_cost_estimate_5yr_usd
- mpg
- insurance_usd_yr
- maint_usd_yr
- co2_g_km
- electric_range_mi
- charge_speed_kw

---

Each score must:

    Be a float between -1.0000 and +1.0000
    Use four decimal places
    Default to 0.0000 if data is ambiguous or unknown

📊 SCORING GUIDE — EXPLICIT THRESHOLDS + REAL CAR EXAMPLES
🔧 PERFORMANCE & RIDE
  handling_rating
      -1.0000: Toyota Sienna (sloppy)
      0.0000: Honda Accord
      +1.0000: Porsche Cayman (sharp)

  braking_dist_ft
      -1.0000: Jeep Gladiator (>150 ft)
      0.0000: Mazda3 (~125 ft)
      +1.0000: Ferrari 296 GTB (<105 ft)

  ride_comfort_rating
      -1.0000: Jeep Wrangler (bouncy)
      0.0000: Toyota Camry
      +1.0000: Mercedes-Benz S-Class (plush)

  cabin_noise_rating
      -1.0000: Ford Bronco (very loud)
      0.0000: Subaru Outback
      +1.0000: Lexus ES (whisper-quiet)

  shift_smooth_rating
      -1.0000: Mitsubishi Mirage (jerky CVT)
      0.0000: Toyota Corolla
      +1.0000: BMW 5 Series (silky automatic)

  steering_feel_rating
      -1.0000: Nissan Rogue (numb)
      0.0000: Hyundai Elantra
      +1.0000: Mazda MX-5 Miata (engaging)

👥 SPACE & PRACTICALITY
  seats
      -1.0000: Mazda MX-5 (2 seats)
      0.0000: Honda CR-V (5 seats)
      +1.0000: Kia Carnival (8 seats, lounge config)

  cargo_space
      -1.0000: Toyota GR86 (<10 cu ft)
      0.0000: VW Jetta (~15 cu ft)
      +1.0000: Subaru Outback (>35 cu ft)

  rear_space
      -1.0000: Subaru BRZ (<30" legroom)
      0.0000: Hyundai Tucson (~35")
      +1.0000: BMW 7 Series (>40")

  ground_clearance_in
      -1.0000: Chevrolet Corvette (<4")
      0.0000: Toyota RAV4 (~6.5")
      +1.0000: Jeep Wrangler Rubicon (>10")

  turn_radius_ft
      -1.0000: Ford Expedition (>42 ft)
      0.0000: Toyota Camry (~36 ft)
      +1.0000: Smart Fortwo (~22 ft)

🧠 SAFETY & VISIBILITY
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
      +1.0000: Audi Q8 (matrix adaptive LEDs)

  security_rating
      -1.0000: Fiat 500 (basic alarm)
      0.0000: Hyundai Sonata
      +1.0000: Range Rover (immobilizer + GPS lock)

🎵 INFOTAINMENT & FEATURES
  screen_in
      -1.0000: Honda Fit (5" non-touch)
      0.0000: Toyota Camry (~8")
      +1.0000: Tesla Model S (17")

  infotainment_ux_rating
      -1.0000: Lexus NX (trackpad)
      0.0000: Ford Escape
      +1.0000: BMW iDrive 8 or Tesla UI

  smartphone_connect_rating
      -1.0000: Mitsubishi Mirage (no CarPlay)
      0.0000: Hyundai Sonata
      +1.0000: Kia EV6 (wireless CarPlay/Android Auto)

  audio_rating
      -1.0000: Nissan Versa (2 speakers)
      0.0000: Honda Civic (6 speakers)
      +1.0000: Mercedes S-Class (Burmester)

  usb_ports
      -1.0000: Chevrolet Spark (1 port)
      0.0000: Toyota RAV4 (3 ports)
      +1.0000: Kia Telluride (6+ ports)

  comfort_feature_score
      -1.0000: Toyota Yaris (manual seats, no climate zones)
      0.0000: Honda Accord
      +1.0000: Genesis G90 (massaging, ventilated everything)

  convenience_feature_score
      -1.0000: Fiat 500 (no sensors)
      0.0000: Mazda CX-5
      +1.0000: BMW X7 (auto-close doors, parking assist)

🛠️ RELIABILITY & OWNERSHIP EXPERIENCE
  reliability_rating
      -1.0000: Alfa Romeo Giulia
      0.0000: Subaru Forester
      +1.0000: Toyota Corolla

  parts_cost_rating
      -1.0000: BMW 7 Series (expensive parts)
      0.0000: Mazda6
      +1.0000: Toyota Corolla (cheap/easy parts)

  dealer_svc_rating
      -1.0000: Mclaren (poor dealer network)
      0.0000: Ford
      +1.0000: Lexus (top-tier service)

🎨 STYLE & BRAND PERCEPTION
  style_sleek_vs_boxy
      -1.0000: Mercedes G-Class (boxy)
      0.0000: Subaru Legacy
      +1.0000: Audi A7 (sleek, coupe-like)

  style_aggression_rating
      -1.0000: Nissan Leaf (soft design)
      0.0000: Toyota Camry SE
      +1.0000: Lamborghini Aventador SVJ

  style_modernity_rating
      -1.0000: Chevy Express Van (dated)
      0.0000: Honda Accord
      +1.0000: Hyundai Ioniq 6

  interior_luxury_rating
      -1.0000: Nissan Versa
      0.0000: Toyota Highlander
      +1.0000: Mercedes-Maybach

  interior_tech_focus_rating
      -1.0000: Jeep Wrangler (analog dials)
      0.0000: Kia Sorento
      +1.0000: Tesla Model 3

  brand_prestige_rating
      -1.0000: Mitsubishi
      0.0000: Honda
      +1.0000: Porsche
"""

def get_files(model: list):
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
  
  executor_img = concurrent.futures.ThreadPoolExecutor(max_workers=8)
  res_img = list(filter(None, list(executor_img.map(get_file, paths_img))))

  executor_aud = concurrent.futures.ThreadPoolExecutor(max_workers=1)
  res_aud = list(filter(None, list(executor_aud.map(get_file, paths_aud))))

  res_wiki = []

  try:
    res_wiki = [(client.files.upload(file=f"data/car_wiki/{model[0]}/{model[1]}.html"))]
  except Exception as e:
      print(f"Failed wiki for {model}", e)
  print(f"Uploaded files for {model}")
  return [{"file_data": {"file_uri": i.uri}} for i in res_img + res_aud + res_wiki]

def queryllm_evaluate_model(model:  list):
  response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=["Evaluate the model and explain your reasoning for each rating"] + get_files(model),
    config=types.GenerateContentConfig(
      temperature=0.75,
      system_instruction=(system_prompt_car_rate),
      response_mime_type="application/json",
      response_schema=list[car_variables]
    )
  )
  return response

try:
  model = ["BMW", "1 Series"]
  os.makedirs(os.path.dirname(f"data/car_scores/{'/'.join(model)}.json"), exist_ok=True)
  file = open(f"data/car_scores/{'/'.join(model)}.json", "w")
  file.write(queryllm_evaluate_model(model).text)
  file.close()
except Exception as e:
  print(e)