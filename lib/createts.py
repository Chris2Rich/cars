from queryticker import search_cik
from queryllm import queryllm_extract10k
import numpy
import matplotlib.pyplot as plt
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

links = search_cik("aapl")
res = []
for i in links:
    time.sleep(4)
    res.append(queryllm_extract10k(i["data"]))

print(res)
total_revenue = [i["Total_Revenue"] for i in res]
total_revenue.reverse()

plt.plot(total_revenue)
plt.ylabel("Total Revenue")
plt.show()