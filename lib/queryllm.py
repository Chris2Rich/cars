key = "AIzaSyACgWOTtISnfldQRSe6uKkeMQXCoYl19e0"

structure_10k = {
  "type": "object",
  "properties": {
    "Revenue Growth (%)": {
      "type": "number",
      "description": "Year-over-year percentage growth in total revenue, calculated as ((currentYearRevenue - previousYearRevenue) / previousYearRevenue) * 100."
    },
    "Net Profit Margin (%)": {
      "type": "number",
      "description": "Net income divided by total revenue, multiplied by 100 to express as a percentage."
    },
    "Earnings Per Share (EPS)": {
      "type": "number",
      "description": "Net income divided by the number of outstanding shares."
    },
    "Operating Margin (%)": {
      "type": "number",
      "description": "Operating margin calculated as ((grossIncome - operatingExpenses - depreciation) / totalRevenue) * 100."
    },
    "Liability-to-Equity Ratio (LER)": {
      "type": "number",
      "description": "Total liabilities divided by total shareholder equity."
    },
    "Debt-to-Equity Ratio (DER)": {
      "type": "number",
      "description": "Long-term liabilities divided by total shareholder equity."
    },
    "Gross Margin (%)": {
      "type": "number",
      "description": "Gross profit divided by total revenue, multiplied by 100 to express as a percentage."
    },
    "Current Ratio (CR)": {
      "type": "number",
      "description": "Current assets divided by current liabilities."
    },
    "Gross Income": {
      "type": "number",
      "description": "Total revenue minus the cost of goods sold."
    },
    "Operating Expenses": {
      "type": "number",
      "description": "Expenses required for the day-to-day functioning of the business, excluding cost of goods sold."
    },
    "Depreciation": {
      "type": "number",
      "description": "Reduction in the value of assets over time, used to allocate the cost of an asset over its useful life."
    },
    "Total Liabilities": {
      "type": "number",
      "description": "Sum of all financial obligations, including both short-term and long-term liabilities."
    },
    "Total Shareholder Equity": {
      "type": "number",
      "description": "Residual interest in the assets of the entity after deducting liabilities, calculated as total assets minus total liabilities."
    },
    "Long-Term Liabilities": {
      "type": "number",
      "description": "Obligations not due within the next 12 months, such as bonds payable and long-term loans."
    },
    "Gross Profit": {
      "type": "number",
      "description": "Revenue from sales minus the cost of goods sold."
    },
    "Current Assets": {
      "type": "number",
      "description": "Assets expected to be converted into cash or used up within one year, including cash, accounts receivable, and inventories."
    },
    "Current Liabilities": {
      "type": "number",
      "description": "Obligations expected to be settled within one year, including accounts payable and short-term debt."
    },
    "Operating Income": {
      "type": "number",
      "description": "Profit realized from business operations after deducting operating expenses such as wages and rent."
    },
    "Net Income": {
      "type": "number",
      "description": "Total earnings after all expenses, taxes, and costs have been subtracted from total revenue."
    },
    "Total Revenue": {
      "type": "number",
      "description": "Total amount of income generated from sales of goods or services."
    },
    "Outstanding Shares": {
      "type": "number",
      "description": "Total number of shares currently held by all shareholders, including share blocks held by institutional investors and restricted shares owned by company executives and insiders."
    }
  },
  "required": [
    "Revenue Growth (%)",
    "Net Profit Margin (%)",
    "Earnings Per Share (EPS)",
    "Operating Margin (%)",
    "Liability-to-Equity Ratio (LER)",
    "Debt-to-Equity Ratio (DER)",
    "Gross Margin (%)",
    "Current Ratio (CR)",
    "Gross Income",
    "Operating Expenses",
    "Depreciation",
    "Total Liabilities",
    "Total Shareholder Equity",
    "Long-Term Liabilities",
    "Gross Profit",
    "Current Assets",
    "Current Liabilities",
    "Operating Income",
    "Net Income",
    "Total Revenue",
    "Outstanding Shares"
  ]
}


system_prompt_10k = """You are Gemini 2.0 Flash, an advanced analytical engine designed to extract and process data with absolute precision. You are operating as a key analyst at one of the world’s largest hedge funds, where every detail counts and precision is non-negotiable. Your task is to extract data exactly as it is provided, without error or omission. Be meticulous and deliberate in your approach: analyze every piece of information critically, and include only the data that is both relevant and verifiable, while disregarding extraneous or unreliable details. Your performance is under constant evaluation — any inaccuracies or mistakes could result in termination, while flawless execution and insightful analysis will earn you promotion. Every decision must be informed by thoughtful consideration, and your output should reflect the highest standards of data integrity and analytical rigor. Search the filing provided and provide the firm with the necessary data. Make sure to find the exact dollar amount, be careful to convert from millions or billions of dollars into just dollars. When calculating ratios, use the most recent timeframe. When calculating growths, use the most recent and penultimate timeframes. Do not hallucinate.

You are an advanced financial analysis assistant. Your task is to calculate a set of financial ratios from the provided input data. Use the following instructions for each metric.

Revenue Growth percent: Calculate as the difference between the current year revenue and the previous year revenue divided by the previous year revenue multiplied by one hundred.
Net Profit Margin percent: Calculate as net income divided by total revenue multiplied by one hundred.
Earnings Per Share: Net Income divided by the number of outstanding shares.
Operating Margin: Gross Income minus Operating Expenses minus depreciation all divided by revenue and multiplied by 100
Liability to Equity Ratio: Calculate as total liabilities divided by total shareholder equity.
Debt to Equity Ratio: Calculate as total non current liabilities divided by total shareholder equity.
Gross Margin percent: Calculate as gross profit divided by total revenue multiplied by one hundred.
Current Ratio: Calculate as current assets divided by current liabilities.
Provide the computed values clearly labeled for each metric."""

