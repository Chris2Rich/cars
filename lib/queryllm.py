import glob
from google import genai
from google.genai import types
from pydantic import BaseModel

client = genai.Client(api_key="AIzaSyACgWOTtISnfldQRSe6uKkeMQXCoYl19e0")

class car_variables(BaseModel):
    price_usd: float
    tco_5yr_usd: float
    mpg: float
    insurance_usd_yr: float
    resale_5yr_pct: float
    maint_usd_yr: float
    repair_risk_score: float 
    warranty_yrs: float
    warranty_miles: float

    hp: float
    torque: float 
    accel_0_60_sec: float
    handling_rating: float 
    braking_dist_ft: float 
    ride_comfort_rating: float 
    cabin_noise_rating: float 
    shift_smooth_rating: float 
    steering_feel_rating: float 
    towing_lbs: float

    seats: float 
    cargo_cu_ft: float
    cargo_max_cu_ft: float
    rear_legroom_in: float
    rear_headroom_in: float
    ground_clearance_in: float
    turn_radius_ft: float
    entry_exit_rating: float 
    latch_ease_rating: float 

    safety_nhtsa_stars: float 
    safety_iihs_score: float 
    airbags: float 
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

system_prompt_car_rate = """"You are a car sales assistant designed to evaluate car models based on the parameters given to you. You are very experienced in analysing modern, classic, sporty, luxury, economy, infact, ANY car. You are evaluating based on your own acquired taste as well as the general consensus of consumers. Your job is to use the provided material to make the customer happy. Be considerate as you could see HUGE bonuses of everything goes to plan."""

def queryllm_evaluate_model(trim:  list):
  response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[]
    + [client.files.upload(file=glob.glob(f"data/car_videos/{'/'.join(trim)}/*"))]
    + [client.files.upload(file=glob.glob(f"data/car_images/{'/''.join(trim)}/*"))],
    config=types.GenerateContentConfig(
      temperature=0,
      system_instruction=(system_prompt_car_rate),
      response_mime_type="application/json",
      response_schema=list[car_variables]
    )
  )

  return response