import gzip
import json

import matplotlib.pyplot as plt
import pandas as pd

with gzip.open("data.json.gz") as f:
    data = json.load(f)

characters = pd.DataFrame(data["characters"])
sessions = pd.DataFrame(data["sessions"])

print(characters)
print(sessions)
print()

correct = (characters.result == "Correct").sum()
total = len(characters.index)
success_rate = correct / total

print(f"Global success rate: {success_rate * 100:.1f}%")

characters["correct"] = characters.result == "Correct"
w = characters.rolling(window=10000)
correct = w.correct.sum()
total = 10000
success_rate = correct / total
success_rate.plot()

plt.show(block=True)
