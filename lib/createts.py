from queryticker import search_cik
from queryllm import queryllm_extractsec
import numpy
import matplotlib.pyplot as plt
import time
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

links = search_cik("aapl")
print("Fetched data")
res = []

links = links[:3]

token_count = []
last4m = time.time()
for i in range(0, len(links)):
    token_count = [i for i in token_count if time.time() - i[0] < 60]
    if sum([i[1] for i in token_count]) > 4000000:
        time.sleep(2)
    else:
        time.sleep(0.02)
        query = (queryllm_extractsec(links[i]["data"], parsing_10k=True) if "10-K" in links[i]["type"] else queryllm_extractsec(links[i]["data"]))
        token_count.append((time.time(), query.usage_metadata.total_token_count))
        res.append(json.loads(query.text)[0])
        print(f"Done with {i} - {token_count[-1][1]} tokens used")

print(res)
total_revenue = [i["Total_Revenue"] for i in res]
total_revenue.reverse()

plt.plot(total_revenue)
plt.ylabel("Total Revenue")
plt.show()
