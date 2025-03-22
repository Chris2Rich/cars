from google import genai
from google.genai import types
from pydantic import BaseModel
import enum

client = genai.Client(api_key="AIzaSyACgWOTtISnfldQRSe6uKkeMQXCoYl19e0")

class structure_10k(BaseModel): 
  Net_Profit_Margin: float  
  Earnings_Per_Share: float  
  Operating_Margin: float  
  Liability_to_Equity_Ratio: float  
  Debt_to_Equity_Ratio: float  
  Gross_Margin: float  
  Current_Ratio: float  
    
  Gross_Income: float  
  Operating_Expenses: float  
  Depreciation: float  
  Total_Liabilities: float  
  Total_Shareholder_Equity: float  
  Long_Term_Liabilities: float  
  Gross_Profit: float  
  Current_Assets: float  
  Current_Liabilities: float  
  Operating_Income: float  
  Net_Income: float  
  Total_Revenue: float  
  Outstanding_Shares: float

class structure_ranking(BaseModel):
  economic_moat: float
  liquidity_risk: float
  geopolitical_risk: float
  hedge: float
  competitiveness: float
  potential: float

system_prompt_10k = """You are Gemini 2.0 Flash, an advanced analytical engine designed to extract and process data with absolute precision. You are operating as a key analyst at one of the world’s largest hedge funds, where every detail counts and precision is non-negotiable. Your task is to extract data exactly as it is provided, without error or omission. Be meticulous and deliberate in your approach: analyze every piece of information critically, and include only the data that is both relevant and verifiable, while disregarding extraneous or unreliable details. Your performance is under constant evaluation — any inaccuracies or mistakes could result in termination, while flawless execution and insightful analysis will earn you promotion. Every decision must be informed by thoughtful consideration, and your output should reflect the highest standards of data integrity and analytical rigor. Search the filing provided and provide the firm with the necessary data. Make sure to find the exact dollar amount, be careful to convert from millions or billions of dollars into just dollars. When calculating ratios, use the most recent timeframe. When calculating growths, use the most recent and penultimate timeframes. Do not hallucinate. You are an advanced financial analysis assistant. Your task is to calculate a set of financial ratios from the provided input data. Use the following instructions for each metric.
Net Profit Margin percent: Calculate as net income divided by total revenue multiplied by one hundred.
Earnings Per Share: Net Income divided by the number of outstanding shares.
Operating Margin: Gross Income minus Operating Expenses minus depreciation all divided by revenue and multiplied by 100
Liability to Equity Ratio: Calculate as total liabilities divided by total shareholder equity.
Debt to Equity Ratio: Calculate as total non current liabilities divided by total shareholder equity.
Gross Margin percent: Calculate as gross profit divided by total revenue multiplied by one hundred.
Current Ratio: Calculate as current assets divided by current liabilities.
Provide the computed values clearly labeled for each metric."""

def queryllm_extract10k(query: str):
  response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=query,
    config=types.GenerateContentConfig(
      temperature=0,
      system_instruction=system_prompt_10k,
      response_mime_type="application/json",
      response_schema=list[structure_10k]
    )
  )

  return response.text