from queryticker import search_cik
from queryllm import queryllm_extract10k
import numpy
import matplotlib.pyplot as plt
import time
import sys

sys.stdout.reconfigure(encoding="utf-8")

links = search_cik("aapl")
res = []

token_count = 0
for i in range(0, len(links)):
    if token_count > 800000:
        time.sleep(60)
        token_count = 0
    else:
        time.sleep(2)
        token_count += len(links[i]["data"]) / 4
        res.append(queryllm_extract10k(links[i]["data"]))
        print(f"Done with {i} - approximately {token_count} tokens used")

print(res)
total_revenue = [i["Total_Revenue"] for i in res]
total_revenue.reverse()

plt.plot(total_revenue)
plt.ylabel("Total Revenue")
plt.show()